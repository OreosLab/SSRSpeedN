import copy
import json
from abc import ABCMeta, abstractmethod
from typing import Optional, Tuple

import requests
from loguru import logger

from ssrspeed.config import ssrconfig
from ssrspeed.parser.conf import shadowsocks_get_config
from ssrspeed.parser.filter import NodeFilter
from ssrspeed.util import b64plus

LOCAL_ADDRESS = ssrconfig.get("localAddress", "127.0.0.1")
LOCAL_PORT = ssrconfig.get("localPort", 7890)
TIMEOUT = 10


class BottomParser(NodeFilter, metaclass=ABCMeta):
    def __init__(self):
        super().__init__()
        self._config_list: list = []
        self.__base_shadowsocks_config: dict = shadowsocks_get_config()
        self.__base_shadowsocks_config["timeout"]: int = TIMEOUT
        self.__base_shadowsocks_config["local_port"]: int = LOCAL_PORT
        self.__base_shadowsocks_config["local_address"]: str = LOCAL_ADDRESS

    def clean_configs(self):
        self._config_list = []

    def add_configs(self, new_configs: dict):
        for item in new_configs:
            self._config_list.append(item)

    @abstractmethod
    def _parse_link(self, link: str) -> Optional[dict]:
        raise NotImplementedError

    def parse_single_link(self, link: str) -> Optional[dict]:
        return self._parse_link(link)

    @staticmethod
    def _get_local_config() -> Tuple[str, int]:
        return LOCAL_ADDRESS, LOCAL_PORT

    def _get_shadowsocks_base_config(self) -> dict:
        return copy.deepcopy(self.__base_shadowsocks_config)

    def print_node(self):
        for item in self._config_list:
            logger.info(f'{item["group"]} - {item["remarks"]}')

    def read_subscription_config(self, url: str):
        header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
        }
        rep = requests.get(url, headers=header, timeout=15)
        rep.encoding = "utf-8"
        res = rep.content.decode("utf-8").strip()
        links_arr = (b64plus.decode(res).decode("utf-8")).split("\n")
        for link in links_arr:
            link = link.strip()
            if cfg := self._parse_link(link):
                self._config_list.append(cfg)
        logger.info(f"Read {len(self._config_list)} node(s)")

    def read_gui_config(self, filename: str):
        with open(filename, "r", encoding="utf-8") as f:
            for item in json.load(f)["configs"]:
                _dict = {
                    "server": item["server"],
                    "server_port": int(item["server_port"]),
                    "password": item["password"],
                    "method": item["method"],
                    "protocol": item.get("protocol", ""),
                    "protocol_param": item.get("protocolparam", ""),
                    "plugin": item.get("plugin", ""),
                    "obfs": item.get("obfs", ""),
                    "obfs_param": item.get("obfsparam", ""),
                    "plugin_opts": item.get("plugin_opts", ""),
                    "plugin_args": item.get("plugin_args", ""),
                    "remarks": item.get("remarks", item["server"]),
                    "group": item.get("group", "N/A"),
                    "local_address": LOCAL_ADDRESS,
                    "local_port": LOCAL_PORT,
                    "timeout": TIMEOUT,
                    "fast_open": False,
                }
                if _dict["remarks"] == "":
                    _dict["remarks"] = _dict["server"]
                self._config_list.append(_dict)

        logger.info(f"Read {len(self._config_list)} node(s).")

    def get_all_config(self) -> list:
        return self._config_list

    def get_nodes_config(self) -> list:
        return [node.config for node in self.__node_list]

    def get_next_config(self) -> Optional[list]:
        return self._config_list.pop(0) if self._config_list else None
