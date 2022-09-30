import contextlib
from copy import deepcopy
from urllib.parse import parse_qsl, unquote, urlparse

from loguru import logger

from ssrspeed.parser.bottom import BottomParser


class TrojanParser(BottomParser):
    def __init__(self, base_config: dict):
        super().__init__()
        self.__base_config: dict = base_config

    def __get_trojan_base_config(self) -> dict:
        return deepcopy(self.__base_config)

    @staticmethod
    def percent_decode(s: str) -> str:
        try:
            s = unquote(s, encoding="gb2312", errors="strict")
        except Exception:
            with contextlib.suppress(Exception):
                s = unquote(s, encoding="utf8", errors="strict")
        return s

    def _parse_link(self, link: str) -> dict:
        url = urlparse(link.strip("\n"))
        if not url.scheme.startswith("trojan"):
            logger.error(f"Not trojan URL : {link}")
            return {}

        _config = self.__get_trojan_base_config()
        try:
            hostname = url.hostname
            port = url.port or 443
            password = unquote(url.netloc.split("@")[0])
            query = dict(parse_qsl(url.query))
            remarks = unquote(url.fragment)

            _config["remote_addr"], _config["server"] = hostname, hostname
            _config["remote_port"], _config["server_port"] = port, port
            _config["password"][0] = password
            _config["remarks"] = remarks
            _config["ssl"]["verify"] = query.get("allowinsecure", "") == "1"
            _config["ssl"]["sni"] = query.get("sni", "")
            _config["tcp"]["fast_open"] = query.get("tfo", "") == "1"
            _config["group"] = query.get("peer", "N/A")

            # ws protocol must pass host and path
            if query.get("type", "") == "ws":
                _config["websocket"]["enabled"] = "true"
                _config["websocket"]["path"] = query.get("path", "")
                _config["websocket"]["host"] = query.get("host", "")

        except Exception:
            logger.exception(f"Invalid trojan URL : {link}")
        return _config


if __name__ == "__main__":

    from ssrspeed.parser.conf import trojan_get_config

    LINKS = (
        "trojan://8888@[2001:1234:4321:66::33]?allowinsecure=0&tfo=1\n"
        "trojan://123@helloworld.xyz?allowinsecure=0&tfo=1#testIPv4port443\n"
        "trojan://9999@[2001:1234:4321:66::33]:444?allowinsecure=1&tfo=0#testIPv6\n"
        "trojan://1234@a.helloworld.xyz:444?allowinsecure=1&tfo=0#%E4%BD%A0%E5%A5%BD\n"
        "trojan://12345@a.b.c:445?security=tls&sni=a.b.c&alpn=http%2F1.1&type=tcp&headerType=none\n"
        "trojan-go://1@ip.com:446/?sni=qq.com&type=ws&host=fast.com&path=%2Fgo&encryption=ss%3Baes-256-gcm%3Afuckgfw\n"
    )
    tropar = TrojanParser(trojan_get_config())
    for i in LINKS.split("\n"):
        if i:
            print(tropar.parse_single_link(i), "\n")
