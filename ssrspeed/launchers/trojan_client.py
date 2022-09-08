import json
import logging
import subprocess
import sys
from typing import Any, Dict

import aiofiles

from ssrspeed.launchers.base_client import BaseClient
from ssrspeed.paths import KEY_PATH

logger = logging.getLogger("Sub")

CLIENTS_DIR = KEY_PATH["clients"]


# CONFIG_FILE = KEY_PATH["config.json"]


class Trojan(BaseClient):
    def __init__(self, file: str):
        super(Trojan, self).__init__()
        self.config_file: str = f"{file}.json"

    async def start_client(self, config: Dict[str, Any]):
        self._config = config
        async with aiofiles.open(self.config_file, "w+", encoding="utf-8") as f:
            await f.write(json.dumps(self._config))

        if self._process is None:

            if self._platform == "Windows":
                if logger.level == logging.DEBUG:
                    self._process = subprocess.Popen(
                        [
                            f"{CLIENTS_DIR}trojan/trojan.exe",
                            "--config",
                            self.config_file,
                        ]
                    )
                else:
                    self._process = subprocess.Popen(
                        [
                            f"{CLIENTS_DIR}trojan/trojan.exe",
                            "--config",
                            self.config_file,
                        ],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                logger.info(
                    f'Starting trojan with server {config["server"]}:{config["server_port"]}'
                )

            elif self._platform == "Linux" or self._platform == "MacOS":
                if logger.level == logging.DEBUG:
                    self._process = subprocess.Popen(
                        [
                            f"{CLIENTS_DIR}trojan/trojan",
                            "--config",
                            self.config_file,
                        ]
                    )
                else:
                    self._process = subprocess.Popen(
                        [
                            f"{CLIENTS_DIR}trojan/trojan",
                            "--config",
                            self.config_file,
                        ],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                logger.info(
                    f'Starting trojan with server {config["server"]}:{config["server_port"]}'
                )

            else:
                logger.critical(
                    "Your system does not support it. Please contact the developer."
                )
                sys.exit(1)
