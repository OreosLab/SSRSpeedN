import copy
import json

from loguru import logger


class ParserShadowsocksD:
    def __init__(self, base_config):
        self.__config_list: list = []
        self.__base_config = base_config

    def __get_shadowsocks_base_config(self):
        return copy.deepcopy(self.__base_config)

    def parse_subs_config(self, config) -> list:
        ssd_config = json.loads(config)
        group = ssd_config.get("airport", "N/A")
        default_port = int(ssd_config["port"])
        default_method = ssd_config["encryption"]
        default_password = ssd_config["password"]
        default_plugin = ssd_config.get("plugin", "")
        default_plugin_opts = ssd_config.get("plugin_options", "")
        servers = ssd_config["servers"]
        for server in servers:
            _config = self.__get_shadowsocks_base_config()
            _config["server"] = server["server"]
            _config["server_port"] = int(server.get("port", default_port))
            _config["method"] = server.get("encryption", default_method)
            _config["password"] = server.get("password", default_password)
            _config["plugin"] = server.get("plugin", default_plugin)
            _config["plugin_opts"] = server.get("plugin_options", default_plugin_opts)
            _config["group"] = group
            _config["remarks"] = server.get("remarks", server["server"])
            self.__config_list.append(_config)
        logger.info(f"Read {len(self.__config_list)} config(s).")
        return self.__config_list

    @staticmethod
    def parse_gui_config(filename: str):
        raise AttributeError(
            "'parse_gui_config' built-in 'parser_basic.py' with basic shadowsocks parser."
        )
