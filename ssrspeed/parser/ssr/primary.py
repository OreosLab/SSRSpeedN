import copy
from typing import List, Optional

from loguru import logger

from ssrspeed.util import b64plus


class ParserShadowsocksR:
    def __init__(self, base_config: dict):
        self.__base_config: dict = base_config

    def __get_base_config(self) -> dict:
        return copy.deepcopy(self.__base_config)

    def __parse_link(self, link: str) -> Optional[dict]:
        if link[:6] != "ssr://":
            logger.error(f"Unsupported link : {link}")
            return None

        decoded = b64plus.decode(link[6:]).decode("utf-8")
        decoded1 = decoded.split("/?")[0].split(":")[::-1]
        if len(decoded1) != 6:
            return None
        decoded2 = decoded.split("/?")[1].split("&")

        _config = self.__get_base_config()
        _config["server"] = decoded1[5]
        _config["server_port"] = int(decoded1[4])
        _config["method"] = decoded1[2]
        _config["password"] = b64plus.decode(decoded1[0]).decode("utf-8")
        _config["protocol"] = decoded1[3]
        _config["obfs"] = decoded1[1]

        for i in decoded2:
            if "obfsparam" in i:
                _config["obfs_param"] = b64plus.decode(i.split("=")[1]).decode("utf-8")
            elif "protocolparam" in i or "protoparam" in i:
                _config["protocol_param"] = b64plus.decode(i.split("=")[1]).decode(
                    "utf-8"
                )
            elif "remarks" in i:
                _config["remarks"] = b64plus.decode(i.split("=")[1]).decode("utf-8")
            elif "group" in i:
                _config["group"] = b64plus.decode(i.split("=")[1]).decode("utf-8")

        _config["remarks"] = _config.get("remarks", _config["server"])

        return _config

    def parse_single_link(self, link: str) -> Optional[dict]:
        return self.__parse_link(link)

    def parse_gui_data(self, data: dict) -> List[dict]:
        results = []
        for item in data["configs"]:
            _dict = self.__get_base_config()
            _dict["server"] = item["server"]
            _dict["server_port"] = int(item["server_port"])
            _dict["method"] = item["method"]
            _dict["password"] = item["password"]
            _dict["protocol"] = item.get("protocol", "")
            _dict["protocol_param"] = item.get("protocolparam", "")
            _dict["obfs"] = item.get("obfs", "")
            _dict["obfs_param"] = item.get("obfsparam", "")
            _dict["remarks"] = item.get("remarks", item["server"])
            _dict["group"] = item.get("group", "N/A")
            results.append(_dict)
        return results


if __name__ == "__main__":
    LINK = "ssr://NDUuMzIuMTMxLjExMTo4OTg5Om9yaWdpbjphZXMtMjU2LWNmYjpwbGFpbjpiM0JsYm5ObGMyRnRaUS8_cmVtYXJrcz1VMU5TVkU5UFRGOU9iMlJsT3VlLWp1V2J2U0RsaXFEbGlLbm5wb19sc0x6a3Vwcmx0NTdsbktQa3ZaWGxvWjVEYUc5dmNHSG1sYkRtamE3a3VLM2x2NE0mZ3JvdXA9VjFkWExsTlRVbFJQVDB3dVEwOU4"
    print(ParserShadowsocksR({}).parse_single_link(LINK))
