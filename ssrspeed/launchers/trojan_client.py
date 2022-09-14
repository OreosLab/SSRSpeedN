import json
import subprocess
import sys
from typing import Any, Dict

import aiofiles
from loguru import logger

from ssrspeed.config import ssrconfig
from ssrspeed.launchers.base_client import BaseClient

CLIENTS_DIR = ssrconfig["path"]["clients"]


class Trojan(BaseClient):
    def __init__(self, file: str):
        super(Trojan, self).__init__()
        self.config_file: str = f"{file}.json"

    async def start_client(self, config: Dict[str, Any], debug=False):
        self._config = config
        async with aiofiles.open(self.config_file, "w+", encoding="utf-8") as f:
            await f.write(json.dumps(self._config))

        if self._process is None:

            if Trojan._platform == "Windows":
                if debug:
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

            elif Trojan._platform == "Linux" or Trojan._platform == "MacOS":
                if debug:
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
