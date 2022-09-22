import binascii
import copy
import json
from urllib.parse import urlparse

from loguru import logger

from ssrspeed.utils import b64plus


class ParserShadowsocksBasic:
    def __init__(self, base_config: dict):
        self.__config_list: list = []
        self.__base_config: dict = base_config

    def __get_shadowsocks_base_config(self) -> dict:
        return copy.deepcopy(self.__base_config)

    def __decode(self, link_: str) -> dict:
        if not link_.startswith("ss://"):
            raise ValueError(f"Not shadowsocks basic URL : {link_}")
        try:
            link_ = "ss://" + b64plus.decode(link_[5:]).decode("utf-8")
        except binascii.Error:
            raise ValueError(f"Not shadowsocks basic URL : {link_}")
        config = self.__get_shadowsocks_base_config()
        url = urlparse(link_.strip("\n"))
        try:
            encryption, addr_port = url.netloc.split("@")
            if ":" not in addr_port or addr_port.endswith("]"):
                addr = addr_port.strip("[]")
                port = 443
            else:
                addr_port = addr_port.replace("[", "").replace("]", "")
                addr, port = addr_port.rsplit(":", 1)[0], int(
                    addr_port.rsplit(":", 1)[1]
                )
        except Exception:
            raise ValueError(f"Invalid shadowsocks basic URL : {link_}")
        config["server"] = addr
        config["server_port"] = port
        config["method"] = encryption.split(":")[0]
        config["password"] = encryption.split(":")[1]
        config["remarks"] = addr
        return config

    def __parse_link(self, link_: str) -> dict:
        return self.__decode(link_)

    def parse_single_link(self, link: str) -> dict:
        return self.__parse_link(link)

    def parse_subs_config(self, links: list) -> list:
        for link in links:
            link = link.strip()
            if cfg := self.__parse_link(link):
                self.__config_list.append(cfg)
        logger.info(f"Read {len(self.__config_list)} config(s).")
        return self.__config_list

    @staticmethod
    def __get_ssd_group(ssd_subs: list, sub_url: str) -> str:
        if not ssd_subs or not sub_url:
            return "N/A"
        return next(
            (
                item.get("airport", "N/A")
                for item in ssd_subs
                if item.get("url", "") == sub_url
            ),
            "N/A",
        )

    def parse_gui_data(self, data: dict) -> list:
        shadowsocksd_conf = False
        ssd_subs = []
        if "subscriptions" in data:
            shadowsocksd_conf = True
            ssd_subs = data["subscriptions"]
        configs = data["configs"]
        for item in configs:
            _dict = self.__get_shadowsocks_base_config()
            _dict["server"] = item["server"]
            _dict["server_port"] = int(item["server_port"])
            _dict["password"] = item["password"]
            _dict["method"] = item["method"]
            _dict["plugin"] = item.get("plugin", "")
            _dict["plugin_opts"] = item.get("plugin_opts", "")
            _dict["plugin_args"] = item.get("plugin_args", "")
            _dict["remarks"] = item.get("remarks", item["server"])
            if not _dict["remarks"]:
                _dict["remarks"] = _dict["server"]
            _dict["group"] = (
                self.__get_ssd_group(ssd_subs, item.get("subscription_url", ""))
                if shadowsocksd_conf
                else item.get("group", "N/A")
            )

            _dict["fast_open"] = False
            self.__config_list.append(_dict)
        return self.__config_list

    def parse_gui_config(self, filename: str) -> list:
        with open(filename, "r", encoding="utf-8") as f:
            try:
                full_conf = json.load(f)
                self.parse_gui_data(full_conf)
            except json.decoder.JSONDecodeError:
                return []
            except Exception:
                logger.exception("Not Shadowsocks configuration file.")
                return []

        logger.info(f"Read {len(self.__config_list)} node(s).")
        return self.__config_list


if __name__ == "__main__":
    links = (
        "ss://YWVzLTI1Ni1nY206aXN4Lnl0LTMxMDk1NzYxQDE5Mi4yNDEuMTkzLjI0MToxMzU0NQ==\n"
        "ss://YWVzLTEyOC1jZmI6c2hhZG93c29ja3M@156.146.38.163:443#US_13\n"
    )
    sspar = ParserShadowsocksBasic({})
    for link in links.split("\n"):
        if link:
            print(sspar.parse_single_link(link))
