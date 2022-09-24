import yaml
from loguru import logger


class ParserV2RayClash:
    def __init__(self):
        self.__clash_vmess_configs: list = []
        self.__decoded_configs: list = []

    @staticmethod
    def __clash_config_convert(clash_cfg: dict) -> dict:
        server = clash_cfg["server"]
        remarks = clash_cfg.get("name", server)
        group = "N/A"
        port = int(clash_cfg["port"])
        uuid = clash_cfg["uuid"]
        aid = int(clash_cfg["alterId"])
        security = clash_cfg.get("cipher", "auto")
        tls = "tls" if "tls" in clash_cfg else ""  # TLS
        allow_insecure = bool(clash_cfg.get("skip-cert-verify", False))
        net = clash_cfg.get("network", "tcp")  # ws, tcp
        _type = clash_cfg.get("type", "none")  # Obfs type
        ws_header = clash_cfg.get("ws-headers", {})
        headers = {
            header: ws_header[header] for header in ws_header.keys() if header != "Host"
        }
        # http host, web socket host, h2 host, quic encrypt method
        host = ws_header.get("Host", "")
        tls_host = host
        # Websocket path, http path, quic encrypt key
        path = clash_cfg.get("ws-path", "")

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

    def __parse_config(self, clash_cfg: dict):
        for cfg in clash_cfg["proxies"]:
            if cfg.get("type", "N/A").lower() == "vmess":
                self.__clash_vmess_configs.append(cfg)
        for cfg in self.__clash_vmess_configs:
            self.__decoded_configs.append(self.__clash_config_convert(cfg))

    def parse_subs_config(self, config) -> list:
        try:
            clash_cfg = yaml.load(config, Loader=yaml.FullLoader)
        except Exception:
            logger.exception("Not Clash config.")
            return []
        self.__parse_config(clash_cfg)
        return self.__decoded_configs

    def parse_gui_config(self, filename: str) -> list:
        with open(filename, "r+", encoding="utf-8") as f:
            try:
                clash_cfg = yaml.load(f, Loader=yaml.FullLoader)
            except Exception:
                logger.exception("Not Clash config.")
                return []
        self.__parse_config(clash_cfg)
        return self.__decoded_configs


if __name__ == "__main__":
    from ssrspeed.path import ROOT_PATH, get_path_json

    key_path = get_path_json(ROOT_PATH)
    pvc = ParserV2RayClash()
    pvc.parse_gui_config(key_path["data"] + "clash.yaml")
