import logging
import re
from urllib.parse import unquote

from ssrspeed.parsers import BaseParser

logger = logging.getLogger("Sub")


class TrojanParser(BaseParser):
    def __init__(self):
        super(TrojanParser, self).__init__()

    # From: https://github.com/NyanChanMeow/SSRSpeed/issues/105
    def _parse_link(self, link: str) -> dict:
        if not link.startswith("trojan://"):
            logger.error("Unsupported link : {}".format(link))
            return {}

        def percent_decode(s: str) -> str:
            try:
                s = unquote(s, encoding="gb2312", errors="strict")
            except:
                try:
                    s = unquote(s, encoding="utf8", errors="strict")
                except:
                    # error decoding
                    # raise # warning is enough
                    pass
            return s

        link = link[len("trojan://") :]
        if not link:
            return {}

        result: dict = {
            "password": [],
            "remote_addr": "",
            "remote_port": 443,
            "ssl": {"verify": False},
            "tcp": {"fast_open": False},
            "remark": "N/A",
        }
        if "#" in link:
            link, result["remark"] = link.split("#")
        result["remark"] = re.sub(r"\s|\n", "", percent_decode(result["remark"]))

        password = ""
        if "@" in link:
            password, link = link.split("@")
        password = percent_decode(password)
        result["password"].append(password)

        result["remote_addr"], result["remote_port"] = link.split(":")
        res = re.match(r"^\d+", result["remote_port"])
        if res:
            result["remote_port"] = int(res.group(0))

        if "?" in link:
            result["ssl"]["verify"] = (
                link[link.index("?") + len("?allowinsecure=")] == "1"
            )

        if "&" in link:
            result["tcp"]["fast_open"] = link[link.index("&") + len("&tfo=")] == "1"

        return result
