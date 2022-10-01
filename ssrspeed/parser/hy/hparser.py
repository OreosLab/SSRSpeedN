from copy import deepcopy
from urllib.parse import parse_qsl, urlparse

from loguru import logger

from ssrspeed.parser.bottom import BottomParser


class HysteriaParser(BottomParser):
    def __init__(self, base_config: dict):
        super().__init__()
        self.__base_config: dict = base_config

    def __get_hysteria_base_config(self) -> dict:
        return deepcopy(self.__base_config)

    def _parse_link(self, link: str) -> dict:
        url = urlparse(link.strip("\n"))
        if url.scheme != "hysteria":
            logger.error(f"Not hysteria URL : {link}")
            return {}

        _config = self.__get_hysteria_base_config()
        try:
            url = urlparse(link)
            query = dict(parse_qsl(url.query))
            _config["server"] = url.netloc
            _config["hy_server"] = url.hostname
            _config["server_port"] = url.port
            _config["protocol"] = query.get("protocol", "udp")
            _config["up_mbps"] = int(query.get("upmbps", 12))
            _config["down_mbps"] = int(query.get("downmbps", 62))
            _config["obfs"] = query.get("obfsParam")
            _config["auth_str"] = query.get("auth")
            _config["alpn"] = query.get("alpn", "h3")
            _config["server_name"] = query.get("peer")
            _config["insecure"] = bool(query.get("insecure", 1))
            _config["remarks"] = url.fragment or "N/A"
        except Exception:
            logger.exception(f"Invalid hysteria URL : {link}")
        return _config


if __name__ == "__main__":
    from ssrspeed.parser.conf import hysteria_get_config

    hyspar = HysteriaParser(hysteria_get_config())
    print(
        hyspar.parse_single_link(
            "hysteria://1.2.3.4:1?protocol=udp&auth=1&peer=wechat.com&insecure=1&upmbps=12&downmbps=62&alpn=h3#1"
        )
    )
