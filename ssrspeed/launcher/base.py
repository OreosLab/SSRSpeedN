import json
import signal
import subprocess
from typing import Any, Dict, List, Optional

import aiofiles
from loguru import logger

from ssrspeed.util import PLATFORM


class BaseClient:
    _platform: Optional[str] = PLATFORM

    def __init__(self, clients_dir: str, clients: Dict[str, str], file: str):
        self._clients_dir: str = clients_dir
        self._clients: Dict[str, str] = clients
        self._config_file: str = file
        self._config_list: List[Dict[str, Any]] = []
        self._config_str: str = ""
        self._process: Optional[subprocess.Popen[bytes]] = None
        self._cmd: Dict[str, List[str]] = {}

    async def start_client(self, config: Dict[str, Any], debug: bool = False):
        self._config_str = json.dumps(config)
        async with aiofiles.open(self._config_file, "w+", encoding="utf-8") as f:
            await f.write(self._config_str)

        if self._process is None:
            if BaseClient._platform == "Windows":
                self._process = (
                    subprocess.Popen(self._cmd["win_debug"])
                    if debug
                    else subprocess.Popen(
                        self._cmd["win"],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                )

                logger.info(
                    f'Starting {self._clients["win"]} with server {config["server"]}:{config["server_port"]}'
                )

            else:
                self._process = (
                    subprocess.Popen(self._cmd["unix"])
                    if debug
                    else subprocess.Popen(
                        self._cmd["unix_debug"],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                )

                logger.info(
                    f'Starting {self._clients["unix"]} with server {config["server"]}:{config["server_port"]}'
                )

    def check_alive(self) -> bool:
        return self._process.poll() is None  # type: ignore[union-attr]

    # fmt: off
    def stop_client(self):
        if self._process is not None:
            if BaseClient._platform == "Windows":
                self._process.terminate()
            else:
                self._process.send_signal(signal.SIGINT)
        # 	print(self._process.returncode)
            self._process = None
            logger.info("Client terminated.")
    # fmt: on
