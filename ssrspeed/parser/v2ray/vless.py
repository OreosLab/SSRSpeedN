from typing import Optional
from urllib.parse import parse_qsl, urlparse

from loguru import logger

from ssrspeed.util.system import PLATFORM


class ParserV2RayVless:
    @staticmethod
    def parse_subs_config(link: str) -> Optional[dict]:
        try:
            url = urlparse(link)
            query = dict(parse_qsl(url.query))
            netloc = url.netloc
            hostname = url.hostname
            port = url.port
            _type = query["type"]  # Obfs type
            uuid = netloc.split("@")[0]
            host = query.get("host", "")
            path = query.get("path", "")
            tls = query["security"]  # TLS or XTLS
            tls_host = query["sni"]
            alpn = query.get("alpn")
            service_name = query.get("serviceName")
            flow = query.get("flow", "")
            if PLATFORM != "Linux" and "splice" in flow:
                logger.warning("Flow xtls-rprx-splice is only supported on Linux.")
                return None
            remarks = url.fragment or hostname
            group = query.get("group", query.get("url_group", "N/A"))

            logger.debug(
                f"Server : {hostname}, Port : {port}, tls-host : {tls_host}, Path : {path}, "
                f"Type : {_type}, UUID : {uuid}, Network : {_type}, Host : {host}, "
                f"Flow: {flow}, TLS : {tls}, alpn: {alpn}, serviceName: {service_name}, "
                f"Remarks : {remarks}, group={group}"
            )
            return {
                "protocol": "vless",
                "remarks": remarks,
                "server": hostname,
                "server_port": port,
                "id": uuid,
                "type": _type,
                "path": path,
                "network": _type,
                "tls-host": tls_host,
                "host": host,
                "tls": tls,
                "alpn": alpn,
                "serviceName": service_name,
                "flow": flow,
            }

        except Exception:
            logger.exception(f"Parse {link} failed. (V2RayN Vless)")
            return None


if __name__ == "__main__":
    LINKS = """vless://1@a:1?encryption=none&flow=xtls-rprx-direct&security=xtls&sni=a&type=tcp&headerType=none&host=a#1
vless://2@a.b.c:2?encryption=none&flow=xtls-rprx-splice&security=xtls&sni=b&type=tcp&headerType=none&host=a.b.c#2
vless://3@a.b.c:3?encryption=none&security=tls&sni=a.b.c&type=ws&host=c&path=%2F3#3
vless://4@a.b.c:4?encryption=none&security=tls&sni=a.b.c&alpn=h2&type=grpc&serviceName=4grpc&mode=gun#4"""

    for i in LINKS.splitlines():
        print(ParserV2RayVless.parse_subs_config(i))
