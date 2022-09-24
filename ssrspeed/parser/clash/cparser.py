from copy import deepcopy

import yaml
from loguru import logger


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
        _config = self.__get_shadowsocks_base_config()
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
        elif cfg.get("obfs") in ["http", "tls"]:
            plugin = "obfs-local"
        elif cfg.get("obfs"):
            logger.warning(f'Plugin {cfg.get("obfs")} not supported.')
            logger.info(f'Skip {_config["group"]} - {_config["remarks"]}')

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

    @staticmethod
    def __convert_v2ray_cfg(cfg: dict) -> dict:
        server = cfg["server"]
        remarks = cfg.get("name", server)
        group = "N/A"
        port = int(cfg["port"])
        uuid = cfg["uuid"]
        aid = int(cfg["alterId"])
        security = cfg.get("cipher", "auto")
        tls = "tls" if "tls" in cfg else ""  # TLS
        allow_insecure = bool(cfg.get("skip-cert-verify", False))
        net = cfg.get("network", "tcp")  # ws, tcp
        _type = cfg.get("type", "none")  # Obfs type
        ws_header = cfg.get("ws-headers", {})
        headers = {
            header: ws_header[header] for header in ws_header.keys() if header != "Host"
        }
        # http host, web socket host, h2 host, quic encrypt method
        host = ws_header.get("Host", "")
        tls_host = host
        # Websocket path, http path, quic encrypt key
        path = cfg.get("ws-path", "")

        logger.debug(
            f"Server : {server}, Port : {port}, tls-host : {tls_host}, Path : {path}, "
            f"Type : {_type}, UUID : {uuid}, AlterId : {aid}, Network : {net}, "
            f"Host : {host}, TLS : {tls}, Remarks : {remarks}, group={group}"
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

    @staticmethod
    def __convert_trojan_cfg(cfg: dict) -> dict:
        logger.debug(cfg)

        password = cfg["password"]
        server = cfg["server"]
        remarks = cfg.get("name", server)
        group = cfg.get("peer", "N/A")
        sni = cfg.get("sni", "")
        port = int(cfg["port"])
        allow_insecure = bool(cfg.get("skip-cert-verify", False))
        return {
            "run_type": "client",
            "local_addr": "127.0.0.1",
            "local_port": 10870,
            "remote_addr": server,
            "remote_port": port,
            "password": [password],
            "log_level": 1,
            "ssl": {
                "verify": allow_insecure,
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
                "sni": sni,
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
            "group": group,
            "remarks": remarks,
            "server": server,
            "server_port": port,
        }

    def parse_config(self, clash_cfg):
        clash_cfg = yaml.load(clash_cfg, Loader=yaml.FullLoader)
        for cfg in clash_cfg["proxies"]:
            _type = cfg.get("type", "N/A").lower()
            if _type in ["ss", "ssr"]:
                ret = self.__parse_shadowsocks(cfg)
            elif _type == "vmess":
                ret = self.__convert_v2ray_cfg(cfg)
            elif _type == "trojan":
                ret = self.__convert_trojan_cfg(cfg)
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
