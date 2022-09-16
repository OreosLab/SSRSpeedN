import json
import os
import shutil
from typing import Any, Dict

config: Dict[str, Any] = {}


def load_path_config(data: dict):
    config.update(data)


def mkdir(data_dir: str):
    if os.path.exists(data_dir):
        if os.path.isfile(data_dir):
            os.remove(data_dir)
            os.makedirs(data_dir)
    else:
        os.makedirs(data_dir)


def generate_config_file():
    data_dir = config["path"]["data"]
    config_file = config["path"]["ssrspeed.json"]
    config_example_file = config["path"]["ssrspeed.example.json"]
    mkdir(data_dir)
    if os.path.exists(config_file):
        if os.path.isdir(config_file):
            shutil.rmtree(config_file)
            if not os.path.exists(config_example_file):
                raise FileNotFoundError(
                    "Default configuration file not found, please download from the official repo and try again."
                )
            shutil.copy(config_example_file, config_file)
    else:
        if not os.path.exists(config_example_file):
            raise FileNotFoundError(
                "Default configuration file not found, please download from the official repo and try again."
            )
        shutil.copy(config_example_file, config_file)
    with open(config_file, "r", encoding="utf-8") as f:
        file_config = json.load(f)
        config.update(file_config)
