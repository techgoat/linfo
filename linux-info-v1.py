#!/usr/bin/env python3
import argparse
import json
import logging
import os
import time
from langchain_openai import ChatOpenAI
from langchain_community.tools import WikipediaQueryRun, DuckDuckGoSearchRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from dotenv import load_dotenv

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text


load_dotenv()


# llm = ChatOpenAI(
#    model="grok-4",  # grok-4 
#    api_key=os.getenv("XAI_API_KEY"),
#    base_url="https://api.x.ai/v1"
# )


# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('transaction_log.txt'),
        logging.StreamHandler()
    ]
)

HISTORY_FILE = 'query_history.json'

# Rich console for beautiful terminal output
console = Console()

def load_history():
    """Load past queries from JSON file.

    Returns:
        list: List of past query dictionaries.
    """
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    return []

def save_history(history, new_entry):
    """Append new query to history and save to JSON.

    Args:
        history (list): Current history list.
        new_entry (dict): New query entry to add.
    """
    history.append(new_entry)
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=4)
    logging.info(f"Saved new entry to history: {new_entry}")

def validate_inputs(args):
    """Validate CLI arguments.

    Args:
        args (argparse.Namespace): Parsed arguments.

    Raises:
        ValueError: If validation fails.
    """
    if not args.distro:
        raise ValueError("Distribution name is required.")
    if not args.arch:
        raise ValueError("Architecture is required.")
    if args.level and args.level not in ['beginner', 'intermediate', 'advanced']:
        raise ValueError("Expertise level must be one of: beginner, intermediate, advanced.")
    logging.info("Inputs validated successfully.")

def build_prompt(args):
    """Build the agent prompt based on arguments.

    Args:
        args (argparse.Namespace): Parsed arguments.

    Returns:
        str: Formatted prompt string.
    """
    topics = args.topics.split(',') if args.topics else ['basic overview', 'features', 'package management']
    level = args.level or 'general'
    prompt = (
        f"Provide detailed information about the Linux distribution '{args.distro}' "
        f"for the '{args.arch}' architecture. Tailor the response for a {level} user. "
        f"Cover the following topics: {', '.join(topics)}. "
        "Use tools to fetch accurate, up-to-date info. Reason step-by-step."
    )
    logging.info(f"Built prompt: {prompt}")
    return prompt

def run_agent(prompt, api_key):
    """Initialize and run the LLM with tools using a manual tool-calling loop.

    The model may request tools (Wikipedia, DuckDuckGo). We execute them
    and feed results back until the model produces a final text response.

    Args:
        prompt (str): The prompt for the agent.
        api_key (str): XAI API key (loaded via env in caller).

    Returns:
        str: LLM's final response content.
    """
    llm = ChatOpenAI(
        model="grok-4",  # grok-3 or grok-4
        api_key=os.getenv("XAI_API_KEY"),
        base_url="https://api.x.ai/v1"
    )

    tools = [
        WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper()),
        DuckDuckGoSearchRun()
    ]
    tool_map = {tool.name: tool for tool in tools}

    llm_with_tools = llm.bind_tools(tools)
    logging.info("LLM initialized with tools.")

    messages = [HumanMessage(content=prompt)]
    max_iterations = 8
    final_content = ""

    for iteration in range(max_iterations):
        response = llm_with_tools.invoke(messages)
        messages.append(response)

        if not getattr(response, "tool_calls", None):
            # Model returned final answer (no more tool use requested)
            final_content = response.content or ""
            logging.info(f"Final answer received (iteration {iteration}).")
            break

        # Execute any requested tool calls
        for tool_call in response.tool_calls:
            tool_name = tool_call.get("name")
            tool_args = tool_call.get("args", {})
            tool_call_id = tool_call.get("id", "")

            if tool_name in tool_map:
                logging.info(f"Calling tool '{tool_name}' with args: {tool_args}")
                try:
                    # Tools expect a dict or specific input; invoke handles it
                    result = tool_map[tool_name].invoke(tool_args)
                except Exception as e:
                    result = f"ERROR running {tool_name}: {str(e)}"
                    logging.error(result)
            else:
                result = f"Unknown tool requested: {tool_name}"
                logging.warning(result)

            messages.append(
                ToolMessage(content=str(result), tool_call_id=tool_call_id)
            )

    if not final_content:
        # Fallback: last AI message content
        for msg in reversed(messages):
            if isinstance(msg, AIMessage) and msg.content:
                final_content = msg.content
                break

    logging.info(f"LLM final response length: {len(final_content)} chars")
    return final_content

def main():
    """Main function to parse args, run agent, and handle logging/history."""
    parser = argparse.ArgumentParser(description="CLI app for Linux distro info using AI agent.")
    parser.add_argument('--distro', type=str, required=True, help='Linux distribution name (e.g., Ubuntu)')
    parser.add_argument('--arch', type=str, required=True, help='Architecture (e.g., x86_64)')
    parser.add_argument('--level', type=str, choices=['beginner', 'intermediate', 'advanced'], help='Expertise level')
    parser.add_argument('--topics', type=str, help='Comma-separated topics (e.g., features,package_management)')
    args = parser.parse_args()

    try:
        validate_inputs(args)
        history = load_history()
        logging.info(f"Loaded {len(history)} past queries.")

#        api_key = os.getenv('GROQ_API_KEY')
        api_key = os.getenv('XAI_API_KEY')
        if not api_key:
#            raise ValueError("GROQ_API_KEY environment variable not set.")
            raise ValueError("XAI_API_KEY environment variable not set.")

        prompt = build_prompt(args)

        # Run the agent with a nice spinner for better UX
        with console.status(
            f"[bold cyan]Querying {args.distro} ({args.arch})...[/bold cyan]",
            spinner="dots",
            spinner_style="cyan",
        ):
            response = run_agent(prompt, api_key)

        # Beautiful formatted output using Rich
        level = args.level or "general"
        title = Text.assemble(
            ("Linux Distro Info: ", "bold white"),
            (args.distro, "bold cyan"),
            (f"  •  {args.arch}", "dim"),
        )

        subtitle = Text.assemble(
            ("Expertise: ", "dim"),
            (level, "bold yellow"),
            ("   •   Topics: ", "dim"),
            (args.topics or "default", "italic"),
        )

        md = Markdown(response)
        panel = Panel(
            md,
            title=title,
            subtitle=subtitle,
            border_style="bright_blue",
            padding=(1, 2),
            expand=True,
        )

        console.print("\n")  # breathing room
        console.print(panel)
        console.print()  # trailing newline

        new_entry = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'args': vars(args),
            'response': response
        }
        save_history(history, new_entry)

    except Exception as e:
        logging.error(f"Error: {str(e)}")
        error_panel = Panel(
            Text(str(e), style="bold red"),
            title="[bold red]Error[/bold red]",
            border_style="red",
            padding=(1, 2),
        )
        console.print(error_panel)


if __name__ == "__main__":
    main()
