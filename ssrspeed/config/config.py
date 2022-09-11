import json
import os
import shutil
from typing import Any, Dict

from ssrspeed.paths import KEY_PATH

__version__ = "1.3.1"
__web_api_version__ = "0.5.2"

CONFIG_FILE = KEY_PATH["ssrspeed.json"]
CONFIG_EXAMPLE_FILE = KEY_PATH["ssrspeed.example.json"]
config: Dict[str, Any] = {
    "VERSION": __version__,
    "WEB_API_VERSION": __web_api_version__,
}

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
        try:
            file_config = json.load(f)
            config.update(file_config)
        finally:
            pass
    LOADED = True
