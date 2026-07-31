"""LLM agent loop and prompt construction (read-only tools only)."""

from __future__ import annotations

import logging

from langchain_community.tools import DuckDuckGoSearchRun, WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_openai import ChatOpenAI

from linfo.providers import LLMConfig, resolve_llm_config


def build_prompt(args, brief: bool = False, embedded: bool = False) -> str:
    """Build the agent prompt based on arguments.

    Args:
        args: Parsed CLI namespace (needs distro, arch, level, topics).
        brief: If True, request a more concise response (used with --brief).
        embedded: If True, emphasize embedded/IoT/build-system concerns.

    Returns:
        Formatted prompt string.
    """
    topics = (
        args.topics.split(",")
        if args.topics
        else ["basic overview", "features", "package management"]
    )
    level = args.level or "general"

    embedded_extra = ""
    if embedded:
        embedded_extra = (
            " Emphasize embedded/IoT/appliance concerns: build system (Yocto, Buildroot, "
            "image builder), cross-compilation, typical footprint/flash size, init system, "
            "update/OTA mechanisms, licensing notes where relevant, and common hardware targets. "
            "Distinguish build-time vs runtime packaging when applicable."
        )

    if brief:
        prompt = (
            f"Provide a **concise** summary of information about the Linux distribution "
            f"'{args.distro}' for the '{args.arch}' architecture. "
            f"Tailor the response for a {level} user. "
            f"Cover the following topics: {', '.join(topics)}. "
            "Focus on key facts only (e.g. package manager, desktop environments, "
            "target users, pros/cons, official site and download link if relevant). "
            "Keep the total response short and to-the-point. "
            "Use tools to fetch accurate, up-to-date info."
            f"{embedded_extra}"
        )
    else:
        prompt = (
            f"Provide detailed information about the Linux distribution '{args.distro}' "
            f"for the '{args.arch}' architecture. Tailor the response for a {level} user. "
            f"Cover the following topics: {', '.join(topics)}. "
            "Include practical details such as who the distro is best suited for, "
            "key strengths/weaknesses, and any official resources. "
            "Use tools to fetch accurate, up-to-date info. Reason step-by-step."
            f"{embedded_extra}"
        )
    logging.info(f"Built prompt: {prompt}")
    return prompt


def run_agent(
    prompt: str,
    *,
    model: str | None = None,
    config: LLMConfig | None = None,
    provider: str | None = None,
    base_url: str | None = None,
) -> str:
    """Initialize and run the LLM with tools using a manual tool-calling loop.

    The model may request tools (Wikipedia, DuckDuckGo). We execute them
    and feed results back until the model produces a final text response.

    Security note: API key is resolved via providers.resolve_llm_config and
    is never passed into the LLM context or logged.

    Args:
        prompt: The prompt for the agent.
        model: Optional model id override.
        config: Pre-resolved LLMConfig (preferred).
        provider: Provider id if config is not supplied.
        base_url: Base URL override if config is not supplied.

    Returns:
        LLM's final response content.
    """
    llm_cfg = config or resolve_llm_config(
        provider=provider,
        model=model,
        base_url=base_url,
        require_key=True,
    )
    if model:
        # Allow explicit model override even when config was pre-built
        llm_cfg = LLMConfig(
            provider=llm_cfg.provider,
            base_url=llm_cfg.base_url,
            model=model,
            api_key=llm_cfg.api_key,
            requires_key=llm_cfg.requires_key,
            key_source=llm_cfg.key_source,
        )

    if not llm_cfg.api_key and llm_cfg.requires_key:
        raise ValueError("API key missing for agentic mode.")

    logging.info(
        "LLM init provider=%s model=%s base_url=%s key_source=%s",
        llm_cfg.provider,
        llm_cfg.model,
        llm_cfg.base_url,
        llm_cfg.key_source or ("placeholder" if not llm_cfg.requires_key else "unknown"),
    )

    llm = ChatOpenAI(
        model=llm_cfg.model,
        api_key=llm_cfg.api_key or "not-needed",
        base_url=llm_cfg.base_url,
    )

    tools = [
        WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper()),
        DuckDuckGoSearchRun(),
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
            final_content = response.content or ""
            logging.info(f"Final answer received (iteration {iteration}).")
            break

        for tool_call in response.tool_calls:
            tool_name = tool_call.get("name")
            tool_args = tool_call.get("args", {})
            tool_call_id = tool_call.get("id", "")

            if tool_name in tool_map:
                logging.info(f"Calling tool '{tool_name}' with args: {tool_args}")
                try:
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
        for msg in reversed(messages):
            if isinstance(msg, AIMessage) and msg.content:
                final_content = msg.content
                break

    logging.info(f"LLM final response length: {len(final_content)} chars")
    return final_content
