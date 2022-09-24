import contextlib
from copy import deepcopy
from urllib.parse import parse_qsl, unquote, urlparse

from loguru import logger

from ssrspeed.parser.bottom import BottomParser


class TrojanParser(BottomParser):
    def __init__(self):
        super().__init__()
        self.__base_config: dict = {
            "run_type": "client",
            "local_addr": "127.0.0.1",
            "local_port": 10870,
            "remote_addr": "example.com",
            "remote_port": 443,
            "password": ["password1"],
            "log_level": 1,
            "ssl": {
                "verify": "true",
                "verify_hostname": "true",
                "cert": "",
                "cipher": "ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:"
                "ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:"
                "ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:"
                "ECDHE-ECDSA-AES256-SHA:ECDHE-ECDSA-AES128-SHA:"
                "ECDHE-RSA-AES128-SHA:ECDHE-RSA-AES256-SHA:"
                "DHE-RSA-AES128-SHA:DHE-RSA-AES256-SHA:"
                "AES128-SHA:AES256-SHA:DES-CBC3-SHA",
                "cipher_tls13": "TLS_AES_128_GCM_SHA256:TLS_CHACHA20_POLY1305_SHA256:TLS_AES_256_GCM_SHA384",
                "sni": "",
                "alpn": ["h2", "http/1.1"],
                "reuse_session": "true",
                "session_ticket": "false",
                "curves": "",
            },
            "tcp": {
                "no_delay": "true",
                "keep_alive": "true",
                "reuse_port": "false",
                "fast_open": "false",
                "fast_open_qlen": 20,
            },
            "websocket": {"enabled": "false", "path": "", "host": ""},
            "group": "N/A",
        }

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
    LINKS = (
        "trojan://8888@[2001:1234:4321:66::33]?allowinsecure=0&tfo=1\n"
        "trojan://123@helloworld.xyz?allowinsecure=0&tfo=1#testIPv4port443\n"
        "trojan://9999@[2001:1234:4321:66::33]:444?allowinsecure=1&tfo=0#testIPv6\n"
        "trojan://1234@a.helloworld.xyz:444?allowinsecure=1&tfo=0#%E4%BD%A0%E5%A5%BD\n"
        "trojan://12345@a.b.c:445?security=tls&sni=a.b.c&alpn=http%2F1.1&type=tcp&headerType=none\n"
        "trojan-go://1@ip.com:446/?sni=qq.com&type=ws&host=fast.com&path=%2Fgo&encryption=ss%3Baes-256-gcm%3Afuckgfw\n"
    )
    tropar = TrojanParser()
    for i in LINKS.split("\n"):
        if i:
            print(tropar.parse_single_link(i))
