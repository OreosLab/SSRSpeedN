import json
import os
import shutil
from typing import Any, Dict

from ssrspeed import __version__ as version
from ssrspeed.paths import JSON_PATH

config: Dict[str, Any] = {"VERSION": version}

with open(file=JSON_PATH, mode="r", encoding="utf-8") as f:
    config.update({"path": json.load(f)})

CONFIG_FILE = config["path"]["ssrspeed.json"]
CONFIG_EXAMPLE_FILE = config["path"]["ssrspeed.example.json"]

LOADED = False

if not LOADED:
    if os.path.exists(CONFIG_FILE):
        if os.path.isdir(CONFIG_FILE):
            shutil.rmtree(CONFIG_FILE)
            if not os.path.exists(CONFIG_EXAMPLE_FILE):
                raise FileNotFoundError(
                    "Default configuration file not found, please download from the official repo and try again."
                )
            shutil.copy(CONFIG_EXAMPLE_FILE, CONFIG_FILE)
    else:
        if not os.path.exists(CONFIG_EXAMPLE_FILE):
            raise FileNotFoundError(
                "Default configuration file not found, please download from the official repo and try again."
            )
        shutil.copy(CONFIG_EXAMPLE_FILE, CONFIG_FILE)

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        file_config = json.load(f)
        config.update(file_config)

    LOADED = True
