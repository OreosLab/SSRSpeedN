from copy import deepcopy
from typing import Optional

from loguru import logger


class NodeFilter:
    def __init__(self):
        self.__node_list: list = []

    def filter_node(
        self,
        nodes: list,
        kwl: Optional[list] = None,
        gkwl: Optional[list] = None,
        rkwl: Optional[list] = None,
        ekwl: Optional[list] = None,
        egkwl: Optional[list] = None,
        erkwl: Optional[list] = None,
    ) -> list:
        if not kwl:
            kwl = []
        if not gkwl:
            gkwl = []
        if not rkwl:
            rkwl = []
        if not ekwl:
            ekwl = []
        if not egkwl:
            egkwl = []
        if not erkwl:
            erkwl = []
        self.__node_list.clear()
        self.__node_list = deepcopy(nodes)
        self.__filter_node(kwl, gkwl, rkwl)
        self.__exclude_nodes(ekwl, egkwl, erkwl)
        return self.__node_list

    @staticmethod
    def __check_in_list(item: dict, _list: list) -> bool:
        for _item in _list:
            _item = _item.config
            server1 = item.get("server", "")
            server2 = _item.get("server", "")
            port1 = item.get("server_port", item.get("port", 0))
            port2 = _item.get("server_port", _item.get("port", 0))
            if server1 and server2 and port1 and port2:
                if server1 == server2 and port1 == port2:
                    logger.warning(
                        f'{item.get("group", "N/A")} - {item.get("remarks", "N/A")} '
                        f'({item.get("server", "Server EMPTY")}:{item.get("server_port", item.get("port", 0))}) '
                        f"already in list. "
                    )
                    return True
            else:
                return True
        return False

    def __filter_group(self, gkwl: list):
        _list: list = []
        if not gkwl:
            return
        for gkw in gkwl:
            for item in self.__node_list:
                config = item.config
                if self.__check_in_list(config, _list):
                    continue
                if gkw in config["group"]:
                    _list.append(item)
        self.__node_list = _list

    def __filter_remark(self, rkwl: list):
        _list: list = []
        if not rkwl:
            return
        for rkw in rkwl:
            for item in self.__node_list:
                config = item.config
                if self.__check_in_list(config, _list):
                    continue
                if rkw in config["remarks"]:
                    _list.append(item)
        self.__node_list = _list

    def __filter_node(
        self,
        kwl: Optional[list] = None,
        gkwl: Optional[list] = None,
        rkwl: Optional[list] = None,
    ):
        if not kwl:
            kwl = []
        if not gkwl:
            gkwl = []
        if not rkwl:
            rkwl = []
        _list: list = []
        # 	print(len(self.__node_list))
        # 	print(type(kwl))
        if kwl:
            for kw in kwl:
                for item in self.__node_list:
                    config = item.config
                    if self.__check_in_list(config, _list):
                        continue
                    if (kw in config["group"]) or (kw in config["remarks"]):
                        # 	print(item["remarks"])
                        _list.append(item)
            self.__node_list = _list
        self.__filter_group(gkwl)
        self.__filter_remark(rkwl)

    def __exclude_group(self, gkwl: list):
        if not gkwl:
            return
        for gkw in gkwl:
            _list: list = []
            for item in self.__node_list:
                config = item.config
                if self.__check_in_list(config, _list):
                    continue
                if gkw not in config["group"]:
                    _list.append(item)
            self.__node_list = _list

    def __exclude_remark(self, rkwl: list):
        if not rkwl:
            return
        for rkw in rkwl:
            _list: list = []
            for item in self.__node_list:
                config = item.config
                if self.__check_in_list(config, _list):
                    continue
                if rkw not in config["remarks"]:
                    _list.append(item)
            self.__node_list = _list

    def __exclude_nodes(
        self,
        kwl: Optional[list] = None,
        gkwl: Optional[list] = None,
        rkwl: Optional[list] = None,
    ):

        if not kwl:
            kwl = []
        if not gkwl:
            gkwl = []
        if not rkwl:
            rkwl = []
        if kwl:
            for kw in kwl:
                _list: list = []
                for item in self.__node_list:
                    config = item.config
                    if self.__check_in_list(config, _list):
                        continue
                    if (kw not in config["group"]) and (kw not in config["remarks"]):
                        _list.append(item)
                    else:
                        logger.debug(
                            f'Excluded {config["group"]} - {config["remarks"]}'
                        )
                self.__node_list = _list
        self.__exclude_group(gkwl)
        self.__exclude_remark(rkwl)
