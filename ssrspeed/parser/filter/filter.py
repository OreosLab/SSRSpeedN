from copy import deepcopy

from loguru import logger


class NodeFilter:
    def __init__(self):
        self.__node_list: list = []

    def filter_node(self, nodes: list, **kwargs) -> list:
        self.__node_list.clear()
        self.__node_list = deepcopy(nodes)
        if kwargs.get("rs", False):
            self.__get_first_nodes(self.__node_list)
        if kwl := kwargs.get("fk", []):
            self.__filter_node(kwl)
        if gkwl := kwargs.get("frk", []):
            self.__filter_group(gkwl)
        if rkwl := kwargs.get("fgk", []):
            self.__filter_remark(rkwl)
        if ekwl := kwargs.get("ek", []):
            self.__exclude_nodes(ekwl)
        if egkwl := kwargs.get("egk", []):
            self.__exclude_group(egkwl)
        if erkwl := kwargs.get("erk", []):
            self.__exclude_remark(erkwl)
        return self.__node_list

    def __get_first_nodes(self, nodes: list):
        """
        Get the first unique node of node list_dict
        Regardless of order can use
        `list({(d.get("server", ""), d.get("port", 0)): d for d in nodes}.values())`
        """
        existing_dicts = set()
        filtered_list = []
        for node in nodes:
            d = node.config
            if (
                d.get("server", ""),
                d.get("server_port", d.get("port", 0)),
            ) not in existing_dicts:
                existing_dicts.add(
                    (d.get("server", ""), d.get("server_port", d.get("port", 0)))
                )
                filtered_list.append(node)
            else:
                logger.warning(
                    f'{d.get("group", "N/A")} - {d.get("remarks", "N/A")} '
                    f'({d.get("server", "Server EMPTY")}:{d.get("server_port", d.get("port", 0))}) '
                    f"already in list. "
                )
        self.__node_list = filtered_list

    def __filter_node(self, kwl: list):
        self.__node_list = [
            n
            for n in self.__node_list
            if any(kw in n.config["group"] or kw in n.config["remarks"] for kw in kwl)
        ]

    def __filter_group(self, gkwl: list):
        self.__node_list = [
            n for n in self.__node_list if any(kw in n.config["group"] for kw in gkwl)
        ]

    def __filter_remark(self, rkwl: list):
        self.__node_list = [
            n for n in self.__node_list if any(kw in n.config["remarks"] for kw in rkwl)
        ]

    def __exclude_nodes(self, ekwl: list):
        self.__node_list = [
            n
            for n in self.__node_list
            if all(
                kw not in n.config["group"] and kw not in n.config["remarks"]
                for kw in ekwl
            )
        ]

    def __exclude_group(self, egkwl: list):
        self.__node_list = [
            n
            for n in self.__node_list
            if all(kw not in n.config["group"] for kw in egkwl)
        ]

    def __exclude_remark(self, erkwl: list):
        self.__node_list = [
            n
            for n in self.__node_list
            if all(kw not in n.config["remarks"] for kw in erkwl)
        ]
