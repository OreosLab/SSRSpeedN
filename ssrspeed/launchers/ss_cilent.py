import json
import logging
import subprocess
import sys
import time
from typing import Any, Dict, Optional

from ssrspeed.launchers import BaseClient
from ssrspeed.paths import KEY_PATH

logger = logging.getLogger("Sub")

CLIENTS_DIR = KEY_PATH["clients"]
CONFIG_FILE = KEY_PATH["config.json"]


class Shadowsocks(BaseClient):
    def __init__(self):
        super(Shadowsocks, self).__init__()

    def start_client(self, _config: Dict[str, Any]):
        self._config = _config
        #   self._config["server_port"] = int(self._config["server_port"])
        with open(CONFIG_FILE, "w+", encoding="utf-8") as f:
            f.write(json.dumps(self._config))

        if self._process is None:

            if self._platform == "Windows":
                if logger.level == logging.DEBUG:
                    self._process = subprocess.Popen(
                        [
                            f"{CLIENTS_DIR}shadowsocks-libev/ss-local.exe",
                            "-u",
                            "-c",
                            CONFIG_FILE,
                            "-v",
                        ]
                    )
                else:
                    self._process = subprocess.Popen(
                        [
                            f"{CLIENTS_DIR}shadowsocks-libev/ss-local.exe",
                            "-u",
                            "-c",
                            CONFIG_FILE,
                        ],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                logger.info(
                    "Starting Shadowsocks-libev with server %s:%d"
                    % (_config["server"], _config["server_port"])
                )

            elif self._platform == "Linux" or self._platform == "MacOS":
                if logger.level == logging.DEBUG:
                    self._process = subprocess.Popen(
                        [
                            f"{CLIENTS_DIR}shadowsocks-libev/ss-local",
                            "-u",
                            "-v",
                            "-c",
                            CONFIG_FILE,
                        ]
                    )
                else:
                    self._process = subprocess.Popen(
                        [
                            f"{CLIENTS_DIR}shadowsocks-libev/ss-local",
                            "-u",
                            "-c",
                            CONFIG_FILE,
                        ],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                logger.info(
                    "Starting Shadowsocks-libev with server %s:%d"
                    % (_config["server"], _config["server_port"])
                )

            else:
                logger.critical(
                    "Your system does not support it. Please contact the developer."
                )
                sys.exit(1)


class Shadowsockss(BaseClient):
    def __init__(self):
        super(Shadowsockss, self).__init__()

    @staticmethod
    def get_current_config() -> int:
        with open(
            f"{CLIENTS_DIR}shadowsocks-win/gui-config.json", "r", encoding="utf-8"
        ) as f:
            tmp_conf = json.loads(f.read())
        cur_index = tmp_conf["index"]
        return tmp_conf["configs"][cur_index]

    def next_win_conf(self) -> Optional[list]:
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

        logger.info("Wait {} secs to start the client.".format(3))
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

    # fmt: off
    def start_client(self, _config: Dict[str, Any], testing: bool = False):
        if self._process is None:
            
            platform = self._check_platform()
            if platform == "Windows":
                if not testing:
                    self.__win_conf()
            # 	sys.exit(0)
                self._process = subprocess.Popen(
                    [f"{CLIENTS_DIR}shadowsocks-win/Shadowsocks.exe"]
                )
                
            elif platform == "Linux" or platform == "MacOS":
                self._config = _config
                self._config["server_port"] = int(self._config["server_port"])
                with open(CONFIG_FILE, "w+", encoding="utf-8") as f:
                    f.write(json.dumps(self._config))
                if logger.level == logging.DEBUG:
                    self._process = subprocess.Popen(
                        [f"{CLIENTS_DIR}shadowsocks-libev/ss-local", "-v", "-c", CONFIG_FILE]
                    )
                else:
                    self._process = subprocess.Popen(
                        [f"{CLIENTS_DIR}shadowsocks-libev/ss-local", "-c", CONFIG_FILE],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                logger.info(
                    "Starting Shadowsocks-libev with server %s:%d"
                    % (_config["server"], _config["server_port"])
                )
                
            else:
                logger.critical(
                    "Your system does not support it. Please contact the developer."
                )
                sys.exit(1)
    # fmt: on
