"""Query history and transaction logging helpers."""

from __future__ import annotations

import json
import logging
import os

LOGS_DIR = "logs"
os.makedirs(LOGS_DIR, exist_ok=True)

HISTORY_FILE = os.path.join(LOGS_DIR, "query_history.json")


def setup_logging(verbose: bool = False) -> None:
    """Configure logging.

    - Always writes full INFO logs to logs/transaction_log.txt
    - Console (StreamHandler) only receives logs when --verbose is used.
    """
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(logging.INFO)

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    log_path = os.path.join(LOGS_DIR, "transaction_log.txt")
    file_handler = logging.FileHandler(log_path)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    if verbose:
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        stream_handler.setFormatter(formatter)
        root_logger.addHandler(stream_handler)


def load_history() -> list:
    """Load past queries from JSON file.

    Returns:
        List of past query dictionaries.
    """
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return []


def save_history(history: list, new_entry: dict) -> None:
    """Append new query to history and save to JSON.

    Args:
        history: Current history list.
        new_entry: New query entry to add.
    """
    history.append(new_entry)
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)
    logging.info(f"Saved new entry to history: {new_entry}")
