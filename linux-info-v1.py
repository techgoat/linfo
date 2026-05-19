#!/usr/bin/env python3
import argparse
import json
import logging
import os
import time
from langchain_groq import ChatGroq
from langchain_community.tools import WikipediaQueryRun, DuckDuckGoSearchRun
from langchain_community.utilities import WikipediaAPIWrapper

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
    """Initialize and run the LLM with tools.

    Args:
        prompt (str): The prompt for the agent.
        api_key (str): Groq API key.

    Returns:
        str: LLM's final response.
    """
    llm = ChatGroq(temperature=0, groq_api_key=api_key, model_name="llama-3.3-70b-versatile")
    tools = [
        WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper()),
        DuckDuckGoSearchRun()
    ]
    llm_with_tools = llm.bind_tools(tools)
    logging.info("LLM initialized with tools.")
    response = llm_with_tools.invoke(prompt)
    logging.info(f"LLM response: {response.content}")
    return response.content

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

        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable not set.")

        prompt = build_prompt(args)
        response = run_agent(prompt, api_key)

        print("\nDistro Information:\n")
        print(response)

        new_entry = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'args': vars(args),
            'response': response
        }
        save_history(history, new_entry)

    except Exception as e:
        logging.error(f"Error: {str(e)}")
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
