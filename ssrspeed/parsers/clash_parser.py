import logging
from copy import deepcopy

import yaml

logger = logging.getLogger("Sub")


class ClashParser:
    def __init__(self, ss_base_config):
        self.__config_list: list = []
        self.__ss_base_config: dict = ss_base_config

    @property
    def config_list(self) -> list:
        return deepcopy(self.__config_list)

    def __get_shadowsocks_base_config(self) -> dict:
        return deepcopy(self.__ss_base_config)

    def __parse_shadowsocks(self, cfg: dict) -> dict:
        try:
            _dict = self.__get_shadowsocks_base_config()
            _dict["server"] = cfg["server"]
            _dict["server_port"] = int(cfg["port"])
            _dict["password"] = cfg["password"]
            _dict["method"] = cfg["cipher"]
            _dict["remarks"] = cfg.get("name", cfg["server"])
            _dict["group"] = cfg.get("group", "N/A")
            _dict["fast_open"] = False

            p_opts = {}
            plugin = ""
            if cfg.__contains__("plugin"):
                plugin = cfg.get("plugin", "")
                if plugin == "obfs":
                    plugin = "obfs-local"
                elif plugin == "v2ray-plugin":
                    logger.warning("V2Ray plugin not supported.")
                    logger.info("Skip {} - {}".format(_dict["group"], _dict["remarks"]))
                    return {}
                p_opts = cfg.get("plugin-opts", {})
            elif cfg.__contains__("obfs"):
                raw_plugin = cfg.get("obfs", "")
                if raw_plugin:
                    if raw_plugin == "http":
                        plugin = "obfs-local"
                        p_opts["mode"] = "http"
                        p_opts["host"] = cfg.get("obfs-host", "")
                    elif raw_plugin == "tls":
                        plugin = "obfs-local"
                        p_opts["mode"] = "tls"
                        p_opts["host"] = cfg.get("obfs-host", "")
                    else:
                        logger.warning("Plugin {} not supported.".format(raw_plugin))
                        logger.info(
                            "Skip {} - {}".format(_dict["group"], _dict["remarks"])
                        )
                        return {}

            logger.debug("{} - {}".format(_dict["group"], _dict["remarks"]))
            logger.debug(
                "Plugin [{}], mode [{}], host [{}]".format(
                    plugin, p_opts.get("mode", ""), p_opts.get("host", "")
                )
            )
            plugin_opts = ""
            if plugin:
                plugin_opts += (
                    "obfs={}".format(p_opts.get("mode", ""))
                    if p_opts.get("mode", "")
                    else ""
                )
                plugin_opts += (
                    ";obfs-host={}".format(p_opts.get("host", ""))
                    if p_opts.get("host", "")
                    else ""
                )

            _dict["plugin"] = plugin
            _dict["plugin_opts"] = plugin_opts
            _dict["plugin_args"] = ""
            return _dict
        except Exception as e:
            raise e

    @staticmethod
    def __convert_v2ray_cfg(cfg: dict) -> dict:
        server = cfg["server"]
        remarks = cfg.get("name", server)
        group = "N/A"
        port = int(cfg["port"])
        uuid = cfg["uuid"]
        aid = int(cfg["alterId"])
        security = cfg.get("cipher", "auto")
        tls = "tls" if (cfg.get("tls", False)) else ""  # TLS
        allow_insecure = True if (cfg.get("skip-cert-verify", False)) else False
        net = cfg.get("network", "tcp")  # ws,tcp
        _type = cfg.get("type", "none")  # Obfs type
        ws_header = cfg.get("ws-headers", {})
        host = ws_header.get(
            "Host", ""
        )  # http host, web socket host, h2 host, quic encrypt method
        headers = {}
        for header in ws_header.keys():
            if header != "Host":
                headers[header] = ws_header[header]
        tls_host = host
        path = cfg.get("ws-path", "")  # Websocket path, http path, quic encrypt key
        logger.debug(
            "Server : {}, Port : {}, tls-host : {}, Path : {}, Type : {}, UUID : {}, AlterId : {}, Network : {}, "
            "Host : {}, TLS : {}, Remarks : {}, group={}".format(
                server,
                port,
                tls_host,
                path,
                _type,
                uuid,
                aid,
                net,
                host,
                tls,
                remarks,
                group,
            )
        )
        return {
            "remarks": remarks,
            "group": group,
            "server": server,
            "server_port": port,
            "id": uuid,
            "alterId": aid,
            "security": security,
            "type": _type,
            "path": path,
            "allowInsecure": allow_insecure,
            "network": net,
            "headers": headers,
            "tls-host": tls_host,
            "host": host,
            "tls": tls,
        }

    def parse_config(self, clash_cfg):
        clash_cfg = yaml.load(clash_cfg, Loader=yaml.FullLoader)
        for cfg in clash_cfg["proxies"]:
            _type = cfg.get("type", "N/A").lower()
            if _type == "ss":
                ret = self.__parse_shadowsocks(cfg)
            elif _type == "vmess":
                ret = self.__convert_v2ray_cfg(cfg)
            else:
                logger.error(f"Unsupported type {_type}.")
                continue
            if ret:
                self.__config_list.append({"type": _type, "config": ret})

    def parse_gui_config(self, filename):
        with open(filename, "r+", encoding="utf-8") as f:
            try:
                self.parse_config(f.read())
            except:
                logger.exception("Not Clash config.")
