import copy

import yaml
from loguru import logger


class ParserShadowsocksClash:
    def __init__(self, base_config: dict):
        self.__config_list: list = []
        self.__base_config = base_config

    def __get_shadowsocks_base_config(self) -> dict:
        return copy.deepcopy(self.__base_config)

    def __parse_config(self, clash_cfg: dict):
        proxies = clash_cfg.get("proxies", clash_cfg["Proxy"])
        for cfg in proxies:
            if cfg.get("type", "N/A").lower() != "ss":
                logger.info(f'Config {cfg["name"]}, type {cfg["type"]} not supported.')
                continue

            _dict = self.__get_shadowsocks_base_config()
            _dict["server"] = cfg["server"]
            _dict["server_port"] = int(cfg["port"])
            _dict["password"] = cfg["password"]
            _dict["method"] = cfg["cipher"]
            _dict["remarks"] = cfg.get("name", cfg["server"])
            _dict["group"] = cfg.get("group", "N/A")
            _dict["fast_open"] = False

            plugin = cfg.get("plugin")
            if plugin == "obfs":
                plugin = "obfs-local"
            elif plugin == "v2ray-plugin":
                logger.warning("V2Ray plugin not supported.")
                logger.info(f'Skip {_dict["group"]} - {_dict["remarks"]}')
                continue
            elif cfg.get("obfs") in ["http", "tls"]:
                plugin = "obfs-local"
            elif cfg.get("obfs"):
                logger.warning(f'Plugin {cfg.get("obfs")} not supported.')
                logger.info(f'Skip {_dict["group"]} - {_dict["remarks"]}')
                continue

            plugin_opts = ""
            p_opts = cfg.get("plugin-opts", {})
            if mode := p_opts.get("mode") or cfg.get("obfs"):
                plugin_opts += f"obfs={mode}"
            if host := p_opts.get("host") or cfg.get("obfs-host"):
                plugin_opts += f";obfs-host={host}"

            logger.debug(
                f'{_dict["group"]} - {_dict["remarks"]}\n'
                f"Plugin [{plugin}], mode [{mode}], host [{host}]"
            )

            _dict["plugin"] = plugin
            _dict["plugin_opts"] = plugin_opts
            _dict["plugin_args"] = ""
            self.__config_list.append(_dict)

        logger.debug(f"Read {len(self.__config_list)} configs.")

    def parse_subs_config(self, config) -> list:
        try:
            clash_cfg = yaml.load(config, Loader=yaml.FullLoader)
        except Exception:
            logger.exception("Not Clash Subscription.")
            return []

        self.__parse_config(clash_cfg)
        logger.debug(f"Read {len(self.__config_list)} configs.")
        return self.__config_list

    def parse_gui_config(self, filename: str) -> list:
        with open(filename, "r+", encoding="utf-8") as f:
            try:
                clash_cfg = yaml.load(f, Loader=yaml.FullLoader)
            except Exception:
                logger.exception("Not Clash config.")
                return []

        self.__parse_config(clash_cfg)
        logger.debug(f"Read {len(self.__config_list)} configs.")

        return self.__config_list
