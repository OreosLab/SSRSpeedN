import requests
from loguru import logger

from ssrspeed.parsers.base import BaseParser
from ssrspeed.parsers.conf import V2RayBaseConfigs
from ssrspeed.parsers.v2ray import ParserV2RayClash, ParserV2RayN, ParserV2RayQuantumult
from ssrspeed.utils import b64plus


class V2RayParser(BaseParser):
    def __init__(self):
        super(V2RayParser, self).__init__()

    def __generate_config(self, config: dict) -> dict:
        _config = V2RayBaseConfigs.get_config()

        _config["inbounds"][0]["listen"] = self._get_local_config()[0]
        _config["inbounds"][0]["port"] = self._get_local_config()[1]

        # Common
        _config["remarks"] = config["remarks"]
        _config["group"] = config.get("group", "N/A")
        _config["server"] = config["server"]
        _config["server_port"] = config["server_port"]

        # stream settings
        stream_settings = _config["outbounds"][0]["streamSettings"]
        stream_settings["network"] = config["network"]
        if config["network"] == "tcp":
            if config["type"] == "http":
                tcp_settings = V2RayBaseConfigs.get_tcp_object()
                tcp_settings["header"]["request"]["path"] = config["path"].split(",")
                tcp_settings["header"]["request"]["headers"]["Host"] = config[
                    "host"
                ].split(",")
                stream_settings["tcpSettings"] = tcp_settings
        elif config["network"] == "ws":
            web_socket_settings = V2RayBaseConfigs.get_ws_object()
            web_socket_settings["path"] = config["path"]
            web_socket_settings["headers"]["Host"] = config["host"]
            for h in config.get("headers", []):
                web_socket_settings["headers"][h["header"]] = h["value"]
            stream_settings["wsSettings"] = web_socket_settings
        elif config["network"] == "h2":
            http_settings = V2RayBaseConfigs.get_http_object()
            http_settings["path"] = config["path"]
            http_settings["host"] = config["host"].split(",")
            stream_settings["httpSettings"] = http_settings
        elif config["network"] == "quic":
            quic_settings = V2RayBaseConfigs.get_quic_object()
            quic_settings["security"] = config["host"]
            quic_settings["key"] = config["path"]
            quic_settings["header"]["type"] = config["type"]
            stream_settings["quicSettings"] = quic_settings

        stream_settings["security"] = config["tls"]
        if config["tls"] == "tls":
            tls_settings = V2RayBaseConfigs.get_tls_object()
            tls_settings["allowInsecure"] = (
                True if (config.get("allowInsecure", "false") == "true") else False
            )
            tls_settings["serverName"] = config["tls-host"]
            stream_settings["tlsSettings"] = tls_settings

        _config["outbounds"][0]["streamSettings"] = stream_settings

        outbound = _config["outbounds"][0]["settings"]["vnext"][0]
        outbound["address"] = config["server"]
        outbound["port"] = config["server_port"]
        outbound["users"][0]["id"] = config["id"]
        outbound["users"][0]["alterId"] = config["alterId"]
        outbound["users"][0]["security"] = config["security"]
        _config["outbounds"][0]["settings"]["vnext"][0] = outbound
        return _config

    def _parse_link(self, link: str) -> dict:

        if link[:8] != "vmess://":
            logger.error(f"Unsupported link : {link}")
            return {}
        pv2rn = ParserV2RayN()
        cfg = pv2rn.parse_subs_config(link)
        if not cfg:
            pq = ParserV2RayQuantumult()
            cfg = pq.parse_subs_config(link)
        if not cfg:
            logger.error(f"Parse link {link} failed.")
            return {}
        return self.__generate_config(cfg)

    def read_subscription_config(self, url: str):
        header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/39.0.2171.95 Safari/537.36 "
        }
        rep = requests.get(url, headers=header, timeout=15)
        rep.encoding = "utf-8"
        res = rep.content.decode("utf-8")
        try:
            links_arr = (b64plus.decode(res).decode("utf-8")).split("\n")
            for link in links_arr:
                link = link.strip()
                # 	print(link)
                cfg = self._parse_link(link)
                if cfg:
                    # 	print(cfg["remarks"])
                    self._config_list.append(cfg)
        except ValueError:
            logger.info("Try V2Ray Clash Parser.")
            pv2rc = ParserV2RayClash()
            for cfg in pv2rc.parse_subs_config(res):
                self._config_list.append(self.__generate_config(cfg))
        logger.info(f"Read {len(self._config_list)} node(s).")

    def read_gui_config(self, filename):
        pv2rc = ParserV2RayClash()
        v2rnp = ParserV2RayN()
        raw_gui_configs = v2rnp.parse_gui_config(filename)
        if raw_gui_configs is False:
            logger.info("Not V2RayN Config.")
            raw_gui_configs = pv2rc.parse_gui_config(filename)
            if raw_gui_configs is False:
                logger.info("Not Clash Config.")
                logger.critical("Gui config parse failed.")
                raw_gui_configs = []

        for _dict in raw_gui_configs:
            _cfg = self.__generate_config(_dict)
            # 	logger.debug(_cfg)
            self._config_list.append(_cfg)
        logger.info(f"Read {len(self._config_list)} node(s).")


# 	logger.critical("V2RayN configuration file will be support soon.")
