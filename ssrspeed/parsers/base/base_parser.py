import copy
import json
from typing import Optional, Tuple

import requests
from loguru import logger

from ssrspeed.config import ssrconfig
from ssrspeed.parsers.conf import shadowsocks_get_config
from ssrspeed.utils import b64plus

LOCAL_ADDRESS = ssrconfig["localAddress"]
LOCAL_PORT = ssrconfig["localPort"]
TIMEOUT = 10


class BaseParser:
    def __init__(self):
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

    def _parse_link(self, link: str) -> dict:
        return {}

    def parse_single_link(self, link: str) -> dict:
        return self._parse_link(link)

    @staticmethod
    def _get_local_config() -> Tuple[str, int]:
        return LOCAL_ADDRESS, LOCAL_PORT

    def _get_shadowsocks_base_config(self) -> dict:
        return copy.deepcopy(self.__base_shadowsocks_config)

    @staticmethod
    def __check_in_list(item, _list: list) -> bool:
        for _item in _list:
            server1 = item.get("server", "")
            server2 = _item.get("server", "")
            port1 = item.get("server_port", item.get("port", 0))
            port2 = _item.get("server_port", _item.get("port", 0))
            if server1 and server2 and port1 and port2:
                if server1 == server2 and port1 == port2:
                    logger.warning(
                        f'{item.get("group", "N/A")} - {item.get("remarks", "N/A")} '
                        f'({item.get("server", "Server EMPTY")}:{item.get("server_port", item.get("port", 0))}) '
                        f"already in list."
                    )
                    return True
            else:
                return True
        return False

    def __filter_group(self, gkwl: list):
        _list: list = []
        if not gkwl:
            return
        for gkw in gkwl:
            for item in self._config_list:
                if self.__check_in_list(item, _list):
                    continue
                if gkw in item["group"]:
                    _list.append(item)
        self._config_list = _list

    def __filter_remark(self, rkwl: list):
        _list: list = []
        if not rkwl:
            return
        for rkw in rkwl:
            for item in self._config_list:
                if self.__check_in_list(item, _list):
                    continue
                # 	print(item["remarks"])
                if rkw in item["remarks"]:
                    _list.append(item)
        self._config_list = _list

    def filter_node(
        self,
        kwl: Optional[list] = None,
        gkwl: Optional[list] = None,
        rkwl: Optional[list] = None,
    ):
        if not kwl:
            kwl = []
        if not gkwl:
            gkwl = []
        if not rkwl:
            rkwl = []
        _list: list = []
        # 	print(len(self._config_list))
        # 	print(type(kwl))
        if kwl:
            for kw in kwl:
                for item in self._config_list:
                    if self.__check_in_list(item, _list):
                        continue
                    if (kw in item["group"]) or (kw in item["remarks"]):
                        # 	print(item["remarks"])
                        _list.append(item)
            self._config_list = _list
        self.__filter_group(gkwl)
        self.__filter_remark(rkwl)

    def __exclude_group(self, gkwl: Optional[list]):
        if not gkwl:
            return
        for gkw in gkwl:
            _list: list = []
            for item in self._config_list:
                if self.__check_in_list(item, _list):
                    continue
                if gkw not in item["group"]:
                    _list.append(item)
            self._config_list = _list

    def __exclude_remark(self, rkwl: Optional[list]):
        if not rkwl:
            return
        for rkw in rkwl:
            _list: list = []
            for item in self._config_list:
                if self.__check_in_list(item, _list):
                    continue
                if rkw not in item["remarks"]:
                    _list.append(item)
            self._config_list = _list

    def exclude_node(
        self,
        kwl: Optional[list] = None,
        gkwl: Optional[list] = None,
        rkwl: Optional[list] = None,
    ):
        # 	print((kw,gkw,rkw))
        # 	print(len(self._config_list))
        # 	print(self._config_list)
        if not kwl:
            kwl = []
        if not gkwl:
            gkwl = []
        if not rkwl:
            rkwl = []
        if kwl:
            for kw in kwl:
                _list: list = []
                for item in self._config_list:
                    if self.__check_in_list(item, _list):
                        continue
                    if (kw not in item["group"]) and (kw not in item["remarks"]):
                        _list.append(item)
                    else:
                        logger.debug(f'Excluded {item["group"]} - {item["remarks"]}')
                self._config_list = _list
        self.__exclude_group(gkwl)
        self.__exclude_remark(rkwl)

    # 	print(self._config_list)

    def print_node(self):
        for item in self._config_list:
            # 	print(f'{item["group"]} - {item["remarks"]}')
            logger.info(f'{item["group"]} - {item["remarks"]}')

    def read_subscription_config(self, url: str):
        header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/39.0.2171.95 Safari/537.36 "
        }
        rep = requests.get(url, headers=header, timeout=15)
        rep.encoding = "utf-8"
        res = rep.content.decode("utf-8").strip()
        links_arr = (b64plus.decode(res).decode("utf-8")).split("\n")
        for link in links_arr:
            link = link.strip()
            # 	print(link)
            cfg = self._parse_link(link)
            if cfg:
                # 	print(cfg["remarks"])
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
                # 	logger.info(_dict["server"])
                self._config_list.append(_dict)

        logger.info(f"Read {len(self._config_list)} node(s).")

    def get_all_config(self) -> list:
        return self._config_list

    def get_next_config(self) -> Optional[list]:
        if self._config_list:
            return self._config_list.pop(0)
        else:
            return None
