import copy
import logging

import yaml

logger = logging.getLogger("Sub")


class ParserShadowsocksClash(object):
    def __init__(self, base_config):
        self.__config_list: list = []
        self.__base_config = base_config

    def __get_shadowsocks_base_config(self):
        return copy.deepcopy(self.__base_config)

    def __parse_config(self, clash_cfg: dict):
        proxies = (
            clash_cfg["proxies"]
            if clash_cfg.get("proxies", None) is not None
            else clash_cfg["Proxy"]
        )
        for cfg in proxies:
            if cfg.get("type", "N/A").lower() != "ss":
                logger.info(
                    "Config {}, type {} not supported.".format(cfg["name"], cfg["type"])
                )
                continue

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
                    continue
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
                        continue

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

            self.__config_list.append(_dict)

    # 	logger.debug("Read {} configs.".format(
    # 		len(self.__config_list)
    # 		)
    # 	)

    def parse_subs_config(self, config) -> list:
        try:
            clash_cfg = yaml.load(config, Loader=yaml.FullLoader)
        except:
            logger.exception("Not Clash Subscription.")
            return []

        self.__parse_config(clash_cfg)
        # 	logger.debug("Read {} configs.".format(
        # 		len(self.__config_list)
        # 		)
        # 	)
        return self.__config_list

    def parse_gui_config(self, filename: str) -> list:
        with open(filename, "r+", encoding="utf-8") as f:
            try:
                clash_cfg = yaml.load(f, Loader=yaml.FullLoader)
            except:
                logger.exception("Not Clash config.")
                return []

        self.__parse_config(clash_cfg)
        logger.debug("Read {} configs.".format(len(self.__config_list)))

        return self.__config_list
