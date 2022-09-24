import contextlib
import json
from typing import Optional, Union

from loguru import logger

from ssrspeed.util import b64plus


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
            cfg_version = str(_conf.get("v", "1"))
            server = _conf["add"]
            port = int(_conf["port"])
            _type = _conf.get("type", "none")  # Obfs type
            uuid = _conf["id"]
            aid = int(_conf["aid"])
            net = _conf["net"]
            host = ""
            path = ""
            if cfg_version == "2":
                host = _conf.get(
                    "host", ""
                )  # http host, web socket host, h2 host, quic encrypt method
                path = _conf.get(
                    "path", ""
                )  # Websocket path, http path, quic encrypt key
            else:
                with contextlib.suppress(IndexError):
                    host = _conf.get("host", ";").split(";")[0]
                    path = _conf.get("host", ";").split(";")[1]
            tls = _conf.get("tls", "none")  # TLS
            tls_host = host
            security = _conf.get("security", "auto")
            remarks = _conf.get("ps", server)
            group = _conf.get("group", _conf.get("url_group", "N/A"))

            logger.debug(
                f"Server : {server}, Port : {port}, tls-host : {tls_host}, Path : {path}, "
                f"Type : {_type}, UUID : {uuid}, AlterId : {aid}, Network : {net}, "
                f"Host : {host}, TLS : {tls}, Remarks : {remarks}, group={group}"
            )
            return {
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

        except Exception:
            logger.exception(f"Parse {raw_link} failed. (V2RayN Method)")
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
                "group": item.get("group", item.get("url_group", "N/A")),
            }
            if sub_id := _dict["subId"]:
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
                logger.exception("Not V2RayN Config.")
                return False
        return self.parse_gui_data(config)


if __name__ == "__main__":
    LINK = "vmess://eyJhZGQiOiAiczM1NC5va2dnbm9kZS50b3AiLCAiYWlkIjogIjAiLCAiaG9zdCI6ICJzMzU0Lm9rZ2dub2RlLnRvcCIsICJpZCI6ICJlNDgzMmNhMC1kNmY2LTMyYzgtODdkYS1mM2VjY2ZmZTczYzAiLCAibmV0IjogIndzIiwgInBhdGgiOiAiL3BhbmVsbXlhZG1pbiIsICJwb3J0IjogIjMzOTU0IiwgInBzIjogImdpdGh1Yi5jb20vZnJlZWZxIC0gXHU0ZTJkXHU1NmZkXHU5NjNmXHU5MWNjXHU0ZTkxIDEiLCAic2VjdXJpdHkiOiAibm9uZSIsICJ0bHMiOiAidGxzIiwgInR5cGUiOiAiIiwgInVybF9ncm91cCI6ICJ0Lm1lL3JpcGFvamllZGlhbiIsICJ2IjogIjIifQ=="
    print(ParserV2RayN().parse_subs_config(LINK))
