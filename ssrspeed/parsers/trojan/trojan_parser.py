import re
from urllib.parse import unquote

from loguru import logger

from ssrspeed.parsers.base import BaseParser


class TrojanParser(BaseParser):
    def __init__(self):
        super(TrojanParser, self).__init__()

    # From: https://github.com/NyanChanMeow/SSRSpeed/issues/105
    def _parse_link(self, link: str) -> dict:
        if not link.startswith("trojan://"):
            logger.error(f"Unsupported link : {link}")
            return {}

        def percent_decode(s: str) -> str:
            try:
                s = unquote(s, encoding="gb2312", errors="strict")
            except Exception:
                try:
                    s = unquote(s, encoding="utf8", errors="strict")
                except Exception:
                    # error decoding
                    # raise # warning is enough
                    pass
            return s

        link = link[len("trojan://") :]
        if not link:
            return {}

        result: dict = {
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
                "cipher": "ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-CHACHA20-POLY1305"
                ":ECDHE-RSA-CHACHA20-POLY1305:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384"
                ":ECDHE-ECDSA-AES256-SHA:ECDHE-ECDSA-AES128-SHA:ECDHE-RSA-AES128-SHA:ECDHE-RSA-AES256-SHA"
                ":DHE-RSA-AES128-SHA:DHE-RSA-AES256-SHA:AES128-SHA:AES256-SHA:DES-CBC3-SHA",
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

        link = percent_decode(link)
        if "#" in link:
            link, result["remarks"] = link.split("#")
        result["remarks"] = re.sub(r"\s", "", result["remarks"])

        password = ""
        if "@" in link:
            password, link = link.split("@")
        result["password"].append(password)

        host = ""
        if "?" in link:
            host, link = link.split("?")
        result["server"], result["server_port"] = host.split(":")
        p = re.match(r"^\d+", result["server_port"])
        assert p is not None
        result["server_port"] = int(p.group(0))

        result["remote_addr"] = result["server"]
        result["remote_port"] = result["server_port"]

        if link:
            link_args = dict(str.lower(x).split("=") for x in link.split("&"))
            if "allowinsecure" in link_args:
                result["ssl"]["verify"] = link_args["allowinsecure"] == "1"
            if "sni" in link_args:
                result["ssl"]["sni"] = link_args["sni"]
            if "tfo" in link_args:
                result["tcp"]["fast_open"] = link_args["tfo"] == "1"
            if "peer" in link_args:
                result["group"] = link_args["peer"]
            # ws 协议必传 host 与 path
            if (
                "type" in link_args
                and link_args["type"] == "ws"
                and "host" in link_args
                and "path" in link_args
            ):
                result["websocket"]["enabled"] = "true"
                result["websocket"]["path"] = link_args["path"]
                result["websocket"]["host"] = link_args["host"]
        return result
