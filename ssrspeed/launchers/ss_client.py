import json
import subprocess
import sys
import time
from typing import Any, Dict, Optional

import aiofiles
from loguru import logger

from ssrspeed.config import ssrconfig
from ssrspeed.launchers.base_client import BaseClient

CLIENTS_DIR = ssrconfig["path"]["clients"]


class Shadowsocks(BaseClient):
    def __init__(self, file: str):
        super(Shadowsocks, self).__init__()
        self.config_file: str = file

    async def start_client(self, config: Dict[str, Any], debug=False):

        self._config = config
        async with aiofiles.open(self.config_file, "w+", encoding="utf-8") as f:
            await f.write(json.dumps(self._config))

        if self._process is None:

            if Shadowsocks._platform == "Windows":
                if debug:
                    self._process = subprocess.Popen(
                        [
                            f"{CLIENTS_DIR}shadowsocks-libev/ss-local.exe",
                            "-u",
                            "-c",
                            self.config_file,
                            "-v",
                        ]
                    )
                else:
                    self._process = subprocess.Popen(
                        [
                            f"{CLIENTS_DIR}shadowsocks-libev/ss-local.exe",
                            "-u",
                            "-c",
                            self.config_file,
                        ],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                logger.info(
                    f'Starting shadowsocks-libev with server {config["server"]}:{config["server_port"]}'
                )

            elif Shadowsocks._platform == "Linux" or Shadowsocks._platform == "MacOS":
                if debug:
                    self._process = subprocess.Popen(
                        [
                            f"{CLIENTS_DIR}shadowsocks-libev/ss-local",
                            "-u",
                            "-v",
                            "-c",
                            self.config_file,
                        ]
                    )
                else:
                    self._process = subprocess.Popen(
                        [
                            f"{CLIENTS_DIR}shadowsocks-libev/ss-local",
                            "-u",
                            "-c",
                            self.config_file,
                        ],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                logger.info(
                    f'Starting shadowsocks-libev with server {config["server"]}:{config["server_port"]}'
                )

            else:
                logger.critical(
                    "Your system does not support it. Please contact the developer."
                )
                sys.exit(1)


class Shadowsockss(BaseClient):
    def __init__(self, name):
        super(Shadowsockss, self).__init__()
        self.config_file = f"{name}.json"

    @staticmethod
    def get_current_config() -> Dict[str, Any]:
        with open(
            f"{CLIENTS_DIR}shadowsocks-win/gui-config.json", "r", encoding="utf-8"
        ) as f:
            tmp_conf = json.loads(f.read())
        cur_index = tmp_conf["index"]
        return tmp_conf["configs"][cur_index]

    def next_win_conf(self) -> Optional[Dict[str, Any]]:
        self.stop_client()

        with open(
            f"{CLIENTS_DIR}shadowsocks-win/gui-config.json", "r", encoding="utf-8"
        ) as f:
            tmp_conf = json.loads(f.read())
        tmp_conf["configs"] = []
        try:
            cur_config = self._config_list.pop(0)
        except IndexError:
            return None
        tmp_conf["configs"].append(cur_config)

        with open(
            f"{CLIENTS_DIR}shadowsocks-win/gui-config.json", "w+", encoding="utf-8"
        ) as f:
            f.write(json.dumps(tmp_conf))

        logger.info("Wait 3 secs to start the client.")
        for _ in range(0, 6):
            time.sleep(0.5)
        self.start_client({}, True)

        return cur_config

    # 	return tmp_conf["configs"][cur_index]

    def __win_conf(self):
        with open(
            f"{CLIENTS_DIR}shadowsocks-win/gui-config.json", "r", encoding="utf-8"
        ) as f:
            tmp_conf = json.loads(f.read())
        tmp_conf["localPort"] = self._localPort
        tmp_conf["index"] = 0
        tmp_conf["global"] = False
        tmp_conf["enabled"] = False
        tmp_conf["configs"] = []

        for item in self._config_list:
            tmp_conf["configs"].append(item)

        with open(
            f"{CLIENTS_DIR}shadowsocks-win/gui-config.json", "w+", encoding="utf-8"
        ) as f:
            f.write(json.dumps(tmp_conf))

    def start_client(self, config: Dict[str, Any], testing: bool = False, debug=False):
        if self._process is None:

            if Shadowsockss._platform == "Windows":
                if not testing:
                    self.__win_conf()
                # 	sys.exit(0)
                self._process = subprocess.Popen(
                    [f"{CLIENTS_DIR}shadowsocks-win/Shadowsocks.exe"]
                )

            elif Shadowsockss._platform == "Linux" or Shadowsockss._platform == "MacOS":
                self._config = config
                self._config["server_port"] = int(self._config["server_port"])
                with open(self.config_file, "w+", encoding="utf-8") as f:
                    f.write(json.dumps(self._config))
                if debug:
                    self._process = subprocess.Popen(
                        [
                            f"{CLIENTS_DIR}shadowsocks-libev/ss-local",
                            "-v",
                            "-c",
                            self.config_file,
                        ]
                    )
                else:
                    self._process = subprocess.Popen(
                        [
                            f"{CLIENTS_DIR}shadowsocks-libev/ss-local",
                            "-c",
                            self.config_file,
                        ],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                logger.info(
                    f'Starting shadowsocks-libev with server {config["server"]}:{config["server_port"]}'
                )

            else:
                logger.critical(
                    "Your system does not support it. Please contact the developer."
                )
                sys.exit(1)
