import json
import os

def load_config():
    """
    Loads the config file.

    :return: The config dictionary.
    :rtype: dict
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_filepath = os.path.join(script_dir, "config.json")  

    if not os.path.exists(config_filepath):
        raise FileNotFoundError(f"Config file {config_filepath} not found.")
    
    with open(config_filepath, 'r') as f:
        config = json.load(f)
    
    return config