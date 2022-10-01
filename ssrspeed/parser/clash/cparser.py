from copy import deepcopy

import yaml
from loguru import logger

from ssrspeed.util.system import PLATFORM


class ClashParser:
    def __init__(self, ss_config, trojan_config, hysteria_config):
        self.__config_list: list = []
        self.__ss_base_config = ss_config
        self.__trojan_base_config = trojan_config
        self.__hysteria_base_config = hysteria_config

    @property
    def config_list(self) -> list:
        return deepcopy(self.__config_list)

    def __get_ss_base_config(self) -> dict:
        return deepcopy(self.__ss_base_config)

    def __get_trojan_base_config(self) -> dict:
        return deepcopy(self.__trojan_base_config)

    def __get_hysteria_base_config(self) -> dict:
        return deepcopy(self.__hysteria_base_config)

    def __parse_shadowsocks(self, cfg: dict) -> dict:
        _config = self.__get_ss_base_config()
        _config["server"] = cfg["server"]
        _config["server_port"] = int(cfg["port"])
        _config["password"] = cfg["password"]
        _config["method"] = cfg["cipher"]
        _config["remarks"] = cfg.get("name", cfg["server"])
        _config["group"] = cfg.get("group", "N/A")
        _config["fast_open"] = False

        plugin = cfg.get("plugin")
        if plugin == "obfs":
            plugin = "obfs-local"
        elif plugin == "v2ray-plugin":
            logger.warning("V2Ray plugin not supported.")
            logger.info(f'Skip {_config["group"]} - {_config["remarks"]}')
            return {}
        elif cfg.get("obfs") in ["http", "tls"]:
            plugin = "obfs-local"
        elif cfg.get("obfs"):
            logger.warning(f'Plugin {cfg.get("obfs")} not supported.')
            logger.info(f'Skip {_config["group"]} - {_config["remarks"]}')
            return {}

        plugin_opts = ""
        p_opts = cfg.get("plugin-opts", {})
        if mode := p_opts.get("mode") or cfg.get("obfs"):
            plugin_opts += f"obfs={mode}"
        if host := p_opts.get("host") or cfg.get("obfs-host"):
            plugin_opts += f";obfs-host={host}"

        logger.debug(
            f'{_config["group"]} - {_config["remarks"]}\n'
            f"Plugin [{plugin}], mode [{mode}], host [{host}]"
        )

        _config["plugin"] = plugin
        _config["plugin_opts"] = plugin_opts
        _config["plugin_args"] = ""
        return _config

    def __parse_shadowsocksr(self, cfg: dict) -> dict:
        _config = self.__get_ss_base_config()
        _config["server"] = cfg["server"]
        _config["server_port"] = int(cfg["port"])
        _config["method"] = cfg["cipher"]
        _config["password"] = cfg["password"]
        _config["protocol"] = cfg.get("protocol", "")
        _config["protocol_param"] = cfg.get("protocol-param", "")
        _config["obfs"] = cfg.get("obfs", "")
        _config["obfs_param"] = cfg.get("obfs-param", "")
        _config["remarks"] = cfg.get("name", cfg["server"])
        _config["group"] = "N/A"

        return _config

    @staticmethod
    def __convert_vmess_cfg(cfg: dict) -> dict:
        server = cfg["server"]
        remarks = cfg.get("name", server)
        group = "N/A"
        port = int(cfg["port"])
        uuid = cfg["uuid"]
        aid = int(cfg["alterId"])
        security = cfg.get("cipher", "auto")
        tls = "tls" if cfg.get("tls", False) else ""  # TLS
        allow_insecure = bool(cfg.get("skip-cert-verify", False))
        net = cfg.get("network", "tcp")  # ws, tcp
        _type = cfg.get("type", "none")  # Obfs type
        ws_header = cfg.get("ws-headers", cfg.get("ws-opts", {}).get("headers", {}))
        headers = {
            header: ws_header[header] for header in ws_header.keys() if header != "Host"
        }
        # http host, web socket host, h2 host, quic encrypt method
        host = ws_header.get("Host", "")
        tls_host = host
        # Websocket path, http path, quic encrypt key
        path = cfg.get("ws-path", cfg.get("ws-opts", {}).get("path", ""))

        logger.debug(
            f"Server : {server}, Port : {port}, tls-host : {tls_host}, Path : {path}, "
            f"Type : {_type}, UUID : {uuid}, AlterId : {aid}, Network : {net}, "
            f"Host : {host}, TLS : {tls}, Remarks : {remarks}, group={group}"
        )
        return {
            "protocol": "vmess",
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

    @staticmethod
    def __convert_vless_cfg(cfg: dict) -> dict:
        server = cfg["server"]
        remarks = cfg.get("name", server)
        group = "N/A"
        port = int(cfg["port"])
        uuid = cfg["uuid"]
        allow_insecure = bool(cfg.get("skip-cert-verify", False))
        network = cfg.get("network", "tcp")
        alpn = cfg.get("alpn", "h2") if network == "grpc" else ""
        _type = network
        flow = cfg.get("flow", "")
        if PLATFORM != "Linux" and "splice" in flow:
            logger.warning("Flow xtls-rprx-splice is only supported on Linux.")
            return {}
        servername = cfg.get("servername", "")
        tls = "tls" if cfg.get("tls", False) else "xtls"  # TLS or XTLS
        ws_opts = cfg.get("ws-opts", {})
        ws_header = ws_opts.get("headers", {})
        path = ws_opts.get("path", "")
        host = ws_header.get("Host", "")
        tls_host = servername or ws_opts.get("servername", "")
        service_name = cfg.get("grpc-opts", {}).get("grpc-service-name", "")

        logger.debug(
            f"Server : {server}, Port : {port}, tls-host : {tls_host}, Path : {path}, "
            f"Type : {_type}, UUID : {uuid}, Network : {_type}, Host : {host}, "
            f"Flow: {flow}, TLS : {tls}, alpn: {alpn}, serviceName: {service_name}, "
            f"Remarks : {remarks}, group={group}"
        )
        return {
            "protocol": "vless",
            "remarks": remarks,
            "group": group,
            "server": server,
            "server_port": port,
            "id": uuid,
            "type": _type,
            "path": path,
            "allowInsecure": allow_insecure,
            "network": _type,
            "tls-host": tls_host,
            "host": host,
            "tls": tls,
            "alpn": alpn,
            "serviceName": service_name,
            "flow": flow,
        }

    def __parse_trojan(self, cfg: dict) -> dict:
        logger.debug(cfg)

        _config = self.__get_trojan_base_config()
        server = cfg["server"]
        port = int(cfg["port"])
        _config["remote_addr"] = server
        _config["server"] = server
        _config["remote_port"] = port
        _config["server_port"] = port
        _config["password"] = [cfg["password"]]
        _config["ssl"]["verify"] = bool(cfg.get("skip-cert-verify", False))
        _config["ssl"]["sni"] = cfg.get("sni", "")
        _config["remarks"] = cfg.get("name", server)
        _config["group"] = cfg.get("peer", "N/A")
        return _config

    def __parse_hysteria(self, cfg: dict) -> dict:
        logger.debug(cfg)

        _config = self.__get_hysteria_base_config()
        server = cfg["server"]
        port = int(cfg["port"])
        _config["server"] = f"{server}:{port}"
        _config["hy_server"] = server
        _config["server_port"] = port
        _config["protocol"] = cfg.get("protocol", "udp")
        _config["up_mbps"] = int(cfg.get("up", 12))
        _config["down_mbps"] = int(cfg.get("down", 62))
        _config["obfs"] = cfg.get("obfs")
        _config["auth_str"] = cfg.get("auth_str")
        _config["server_name"] = cfg.get("sni")
        _config["insecure"] = cfg.get("skip-cert-verify", True)
        _config["remarks"] = cfg.get("name", server)
        return _config

    def parse_config(self, clash_cfg):
        clash_cfg = yaml.load(clash_cfg, Loader=yaml.FullLoader)
        for cfg in clash_cfg["proxies"]:
            _type = cfg.get("type", "N/A").lower()
            if _type in "ss":
                ret = self.__parse_shadowsocks(cfg)
            elif _type in "ssr":
                ret = self.__parse_shadowsocksr(cfg)
            elif _type in "vless":
                ret = self.__convert_vless_cfg(cfg)
            elif _type == "vmess":
                ret = self.__convert_vmess_cfg(cfg)
            elif _type == "trojan":
                ret = self.__parse_trojan(cfg)
            elif _type == "hysteria":
                ret = self.__parse_hysteria(cfg)
            else:
                logger.error(f"Unsupported type {_type}.")
                continue
            if ret:
                self.__config_list.append({"type": _type, "config": ret})

    def parse_gui_config(self, filename):
        with open(filename, "r+", encoding="utf-8") as f:
            try:
                self.parse_config(f.read())
            except Exception:
                logger.exception("Not Clash config.")
