from loguru import logger

from ssrspeed.parsers.base import BaseParser
from ssrspeed.utils import b64plus


class ShadowsocksRParser(BaseParser):
    def __init__(self):
        super(ShadowsocksRParser, self).__init__()

    def _parse_link(self, link: str) -> dict:
        _config = self._get_shadowsocks_base_config()
        # 	print(self._baseShadowsocksConfig["remarks"])
        if link[:6] != "ssr://":
            logger.error(f"Unsupported link : {link}")
            return {}

        link = link[6:]
        decoded = b64plus.decode(link).decode("utf-8")
        decoded1 = decoded.split("/?")[0].split(":")[::-1]
        if len(decoded1) != 6:
            return {}
        """
            addr = ""
            for i in range(5, len(decoded1) - 1):
                addr += decoded1[i] + ":"
            addr += decoded1[len(decoded1) - 1]
            decoded1[5] = addr
        """
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
