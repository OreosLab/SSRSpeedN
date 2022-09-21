import contextlib
import sys
from copy import deepcopy
from urllib.parse import parse_qsl, unquote, urlparse

from loguru import logger

from ssrspeed.parsers.base import BaseParser


class TrojanParser(BaseParser):
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

    def decode(self, link_: str) -> tuple:
        config = self.__get_trojan_base_config()
        url = urlparse(link_.strip("\n"))
        if not url.scheme.startswith("trojan"):
            logger.error(f"Not trojan URL : {link_}")
            sys.exit(1)
        try:
            password, addr_port = url.netloc.split("@")
            password = unquote(password)
            if ":" not in addr_port or addr_port.endswith("]"):
                addr = addr_port.strip("[]")
                port = 443
            else:
                addr_port = addr_port.replace("[", "").replace("]", "")
                addr, port = addr_port.rsplit(":", 1)[0], int(
                    addr_port.rsplit(":", 1)[1]
                )
            query = dict(parse_qsl(url.query))
            remarks = unquote(url.fragment)
        except:
            logger.error(f"Invalid trojan URL : {link_}")
            sys.exit(1)
        config["remote_addr"], config["server"] = addr, addr
        config["remote_port"], config["server_port"] = port, port
        config["password"][0] = password
        config["remarks"] = remarks
        return config, query

    def _parse_link(self, link_: str) -> dict:
        result, query = self.decode(self.percent_decode(link_))
        result["ssl"]["verify"] = query.get("allowinsecure", "") == "1"
        result["ssl"]["sni"] = query.get("sni", "")
        result["tcp"]["fast_open"] = query.get("tfo", "") == "1"
        result["group"] = query.get("peer", "N/A")

        # ws protocol must pass host and path
        if query.get("type", "") == "ws":
            result["websocket"]["enabled"] = "true"
            result["websocket"]["path"] = query.get("path", "")
            result["websocket"]["host"] = query.get("host", "")
        return result


if __name__ == "__main__":
    links = (
        "trojan://8888@[2001:1234:4321:66::33]?allowinsecure=0&tfo=1\n"
        "trojan://123@helloworld.xyz?allowinsecure=0&tfo=1#testIPv4port443\n"
        "trojan://9999@[2001:1234:4321:66::33]:444?allowinsecure=1&tfo=0#testIPv6\n"
        "trojan://1234@a.helloworld.xyz:444?allowinsecure=1&tfo=0#%E4%BD%A0%E5%A5%BD\n"
        "trojan://12345@a.b.c:445?security=tls&sni=a.b.c&alpn=http%2F1.1&type=tcp&headerType=none\n"
        "trojan-go://1@ip.com:446/?sni=qq.com&type=ws&host=fast.com&path=%2Fgo&encryption=ss%3Baes-256-gcm%3Afuckgfw\n"
    )
    tropar = TrojanParser()
    for link in links.split("\n"):
        if link:
            print(tropar.parse_single_link(link))
