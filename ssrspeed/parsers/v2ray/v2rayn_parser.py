import json
from typing import Optional, Union

from loguru import logger

from ssrspeed.utils import b64plus


class ParserV2RayN:
    def __init__(self):
        self.__decoded_configs = []

    @staticmethod
    def parse_subs_config(raw_link: str) -> Optional[dict]:
        link = raw_link[8:]
        link_decoded = b64plus.decode(link).decode("utf-8")
        try:
            _conf = json.loads(link_decoded)
        except json.JSONDecodeError:
            return None
        try:
            # logger.debug(_conf)
            cfg_version = str(_conf.get("v", "1"))
            server = _conf["add"]
            port = int(_conf["port"])
            _type = _conf.get("type", "none")  # Obfs type
            uuid = _conf["id"]
            aid = int(_conf["aid"])
            net = _conf["net"]
            group = "N/A"
            path = ""
            host = ""
            if cfg_version == "2":
                host = _conf.get(
                    "host", ""
                )  # http host, web socket host, h2 host, quic encrypt method
                path = _conf.get(
                    "path", ""
                )  # Websocket path, http path, quic encrypt key
            # V2RayN Version 1 Share Link Support
            else:
                try:
                    host = _conf.get("host", ";").split(";")[0]
                    path = _conf.get("host", ";").split(";")[1]
                except IndexError:
                    pass
            tls = _conf.get("tls", "none")  # TLS
            tls_host = host
            security = _conf.get("security", "auto")
            remarks = _conf.get("ps", server)
            remarks = remarks if remarks else server
            logger.debug(
                f"Server : {server}, Port : {port}, tls-host : {tls_host}, Path : {path}, "
                f"Type : {_type}, UUID : {uuid}, AlterId : {aid}, Network : {net}, "
                f"Host : {host}, TLS : {tls}, Remarks : {remarks}, group={group}"
            )
            _config = {
                "remarks": remarks,
                "server": server,
                "server_port": port,
                "id": uuid,
                "alterId": aid,
                "security": security,
                "type": _type,
                "path": path,
                "network": net,
                "tls-host": tls_host,
                "host": host,
                "tls": tls,
            }
            return _config
        except Exception:
            logger.error(f"Parse {raw_link} failed. (V2RayN Method)", exc_info=True)
            return None

    def parse_gui_data(self, data: dict) -> list:
        sub_list = data.get("subItem", [])
        for item in data["vmess"]:
            _dict = {
                "server": item["address"],
                "server_port": item["port"],
                "id": item["id"],
                "alterId": item["alterId"],
                "security": item.get("security", "auto"),
                "type": item.get("headerType", "none"),
                "path": item.get("path", ""),
                "network": item["network"],
                "host": item.get("requestHost", ""),
                "tls": item.get("streamSecurity", ""),
                "allowInsecure": item.get("allowInsecure", ""),
                "subId": item.get("subid", ""),
                "remarks": item.get("remarks", item["address"]),
                "group": "N/A",
            }
            if not _dict["remarks"]:
                _dict["remarks"] = _dict["server"]
            sub_id = _dict["subId"]
            if sub_id != "":
                for sub in sub_list:
                    if sub_id == sub.get("id", ""):
                        _dict["group"] = sub.get("remarks", "N/A")
            self.__decoded_configs.append(_dict)
        return self.__decoded_configs

    def parse_gui_config(self, filename: str) -> Union[list, bool]:
        with open(filename, "r", encoding="utf-8") as f:
            try:
                config = json.load(f)
            except Exception:
                logger.error("Not V2RayN Config.", exc_info=True)
                return False
        return self.parse_gui_data(config)
