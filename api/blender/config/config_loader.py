import json
import os


def load_config(filepath):
    """Loads the config file.

    Args:
        filepath (str): The path to the config file.

    Raises:
        FileNotFoundError: If the config file is not found.

    Returns:
        json: The loaded config file.
    """
    with open(filepath, "r") as f:
        config = json.load(f)

    return config
