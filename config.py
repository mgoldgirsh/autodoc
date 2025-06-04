from typing import Any
import json 
import os

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")


def read_config() -> dict:
    """Reads the config file in the package directory and loads it into memory.

    Returns:
        dict: the config dictionary that stores the configuration of the autodoc program
    """
    with open(CONFIG_FILE, 'r') as f:
        config = json.loads(f.read())
    
    if config['memory_location'] == "" or config['memory_location'] is None:
        config['memory_location'] = "/tmp/autodoc-snapshots"
    os.makedirs(config['memory_location'], exist_ok=True)

    return config


def write_config(key: str, value: Any) -> dict:
    """Writes a key, vlaue in the config file in the package directory.

    Args: 
        key (str): the key to write into the config
        value (Any): the value to write into the config json

    Returns:
        dict: the updated config dictionary that stores the configuration of the autodoc program
    """
    config = read_config()
    config[key] = value
    with open(CONFIG_FILE, 'w') as f:
        f.write(json.dumps(config, indent=4))

    return config
