import copy
from typing import List, Optional

from loguru import logger

from ssrspeed.utils import b64plus


class ParserShadowsocksR:
    def __init__(self, base_config: dict):
        self.__base_config: dict = base_config

    def __get_base_config(self) -> dict:
        return copy.deepcopy(self.__base_config)

    def parse_single_link(self, link: str) -> Optional[dict]:
        _config = self.__get_base_config()
        # 	print(self._base_shadowsocks_config["remarks"])
        if link[:6] != "ssr://":
            logger.error(f"Unsupported link : {link}")
            return None

        link = link[6:]
        decoded = b64plus.decode(link).decode("utf-8")
        decoded1 = decoded.split("/?")[0].split(":")[::-1]
        if len(decoded1) != 6:
            return None
        # 	addr = ""
        # 	for i in range(5,len(decoded1) - 1):
        # 		addr += decoded1[i] + ":"
        # 	addr += decoded1[len(decoded1) - 1]
        # 	decoded1[5] = addr
        decoded2 = decoded.split("/?")[1].split("&")
        _config["server"] = decoded1[5]
        _config["server_port"] = int(decoded1[4])
        _config["method"] = decoded1[2]
        _config["protocol"] = decoded1[3]
        _config["obfs"] = decoded1[1]
        _config["password"] = b64plus.decode(decoded1[0]).decode("utf-8")
        for ii in decoded2:
            if "obfsparam" in ii:
                _config["obfs_param"] = b64plus.decode(ii.split("=")[1]).decode("utf-8")
            elif "protocolparam" in ii or "protoparam" in ii:
                _config["protocol_param"] = b64plus.decode(ii.split("=")[1]).decode(
                    "utf-8"
                )
            elif "remarks" in ii:
                _config["remarks"] = b64plus.decode(ii.split("=")[1]).decode("utf-8")
            elif "group" in ii:
                _config["group"] = b64plus.decode(ii.split("=")[1]).decode("utf-8")

        if _config["remarks"] == "":
            _config["remarks"] = _config["server"]
        return _config

    def parse_gui_data(self, data: dict) -> List[dict]:
        results = []
        for item in data["configs"]:
            _dict = self.__get_base_config()
            _dict["server"] = item["server"]
            _dict["server_port"] = int(item["server_port"])
            _dict["password"] = item["password"]
            _dict["method"] = item["method"]
            _dict["protocol"] = item.get("protocol", "")
            _dict["protocol_param"] = item.get("protocolparam", "")
            _dict["obfs"] = item.get("obfs", "")
            _dict["obfs_param"] = item.get("obfsparam", "")
            _dict["remarks"] = item.get("remarks", item["server"])
            _dict["group"] = item.get("group", "N/A")
            if not _dict["remarks"]:
                _dict["remarks"] = _dict["server"]
            results.append(_dict)
        return results
