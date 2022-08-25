import json
import logging
import subprocess
import sys
from typing import Any, Dict

from ssrspeed.launchers.base_client import BaseClient
from ssrspeed.paths import KEY_PATH

logger = logging.getLogger("Sub")

CLIENTS_DIR = KEY_PATH["clients"]
CONFIG_FILE = KEY_PATH["config.json"]


class Trojan(BaseClient):
    def __init__(self):
        super(Trojan, self).__init__()

    def start_client(self, _config: Dict[str, Any]):
        self._config = _config
        with open(CONFIG_FILE, "w+", encoding="utf-8") as f:
            f.write(json.dumps(self._config))
        try:

            if self._process is None:

                if self._platform == "Windows":
                    if logger.level == logging.DEBUG:
                        self._process = subprocess.Popen(
                            [
                                f"{CLIENTS_DIR}trojan/win64/trojan.exe",
                                "--config",
                                CONFIG_FILE,
                            ]
                        )
                    else:
                        self._process = subprocess.Popen(
                            [
                                f"{CLIENTS_DIR}trojan/win64/trojan.exe",
                                "--config",
                                CONFIG_FILE,
                            ],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                        )
                    logger.info(
                        "Starting trojan with server %s:%d"
                        % (_config["server"], _config["server_port"])
                    )

                elif self._platform == "Linux":
                    if logger.level == logging.DEBUG:
                        self._process = subprocess.Popen(
                            [
                                f"{CLIENTS_DIR}trojan/win64/trojan.exe",
                                "--config",
                                CONFIG_FILE,
                            ]
                        )
                    else:
                        self._process = subprocess.Popen(
                            [
                                f"{CLIENTS_DIR}trojan/win64/trojan.exe",
                                "--config",
                                CONFIG_FILE,
                            ],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                        )
                    logger.info(
                        "Starting trojan with server %s:%d"
                        % (_config["server"], _config["server_port"])
                    )

                else:
                    logger.critical(
                        "Your system does not support it. Please contact the developer."
                    )
                    sys.exit(1)

        except FileNotFoundError:
            #   logger.exception("")
            logger.error("Trojan Core Not Found !")
            sys.exit(1)
