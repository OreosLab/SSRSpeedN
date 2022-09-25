import time
from typing import Optional

from loguru import logger

from ssrspeed.config import ssrconfig
from ssrspeed.parser.parser import UniversalParser
from ssrspeed.result import ExportResult
from ssrspeed.result.importer import import_result
from ssrspeed.speedtest import SpeedTest


class SSRSpeedCore:
    def __init__(self):
        self.test_method: str = "ST_ASYNC"
        self.proxy_type: str = "SSR"
        self.web_mode: bool = False
        self.colors: str = "origin"
        self.sort_method: str = ""
        self.test_mode: str = "DEFAULT"

        self.__time_stamp_start: float = -1
        self.__time_stamp_stop: float = -1
        self.__parser: UniversalParser = UniversalParser()
        self.__stc: Optional[SpeedTest] = None
        self.__results: list = []
        self.__status: str = "stopped"

    def set_group(self, group: str):
        self.__parser.set_group(group)

    # Web Methods
    @staticmethod
    def web_get_colors() -> str:
        return ssrconfig["exportResult"]["colors"]

    def web_get_status(self) -> str:
        return self.__status

    @staticmethod
    def __generate_web_configs(nodes: list) -> list:
        return [{"type": node.node_type, "config": node.config} for node in nodes]

    def web_read_subscription(self, url: str) -> list:
        if parser := UniversalParser():
            urls = url.split(" ")
            parser.read_subscription(urls)
            return self.__generate_web_configs(parser.nodes)
        return []

    def web_read_config_file(self, filename: str) -> list:
        if parser := UniversalParser():
            parser.read_gui_config(filename)
            return self.__generate_web_configs(parser.nodes)
        return []

    def web_setup(self, **kwargs):
        self.test_method = kwargs.get("testMethod", "ST_ASYNC")
        self.colors = kwargs.get("colors", "origin")
        self.sort_method = kwargs.get("sortMethod", "")
        self.test_mode = kwargs.get("testMode", "TCP_PING")

    def web_set_configs(self, configs: list):
        if self.__parser:
            self.__parser.set_nodes(UniversalParser.web_config_to_node(configs))

    # Console Methods
    def console_setup(
        self,
        test_mode: str,
        test_method: str,
        color: str = "origin",
        sort_method: str = "",
        url: str = "",
        cfg_filename: str = "",
    ):
        self.test_method = test_method
        self.test_mode = test_mode
        self.sort_method = sort_method
        self.colors = color
        if self.__parser:
            if url:
                self.__parser.read_subscription(url.split(" "))
            elif cfg_filename:
                self.__parser.read_gui_config(cfg_filename)
            else:
                raise ValueError("Subscription URL or configuration file must be set!")

    def start_test(self, args):
        self.__time_stamp_start = time.time()
        self.__stc = SpeedTest(args, self.__parser, self.test_method)
        self.__status = "running"
        if self.test_mode == "DEFAULT":
            self.__stc.default_test()
        elif self.test_mode == "TCP_PING":
            self.__stc.ping_only()
        elif self.test_mode == "STREAM":
            self.__stc.stream_only()
        elif self.test_mode == "ALL":
            self.__stc.full_test()
        elif self.test_mode == "WEB_PAGE_SIMULATION":
            self.__stc.web_page_simulation()
        self.__status = "stopped"
        self.__results = self.__stc.get_result()
        self.__time_stamp_stop = time.time()
        self.__export_result()

    def clean_result(self):
        self.__results = []
        if self.__stc:
            self.__stc.reset_status()

    def get_results(self) -> list:
        return self.__results

    def web_get_results(self) -> dict:
        if self.__status == "running":
            status = "running" if self.__stc else "pending"
        else:
            status = self.__status
        return {
            "status": status,
            "current": self.__stc.get_current()
            if (self.__stc and status == "running")
            else {},
            "results": self.__stc.get_result() if self.__stc else [],
        }

    def filter_nodes(self, **kwargs):
        rs = kwargs.get("rs", False)
        fk = kwargs.get("fk", [])
        fgk = kwargs.get("fgk", [])
        frk = kwargs.get("frk", [])
        ek = kwargs.get("ek", [])
        egk = kwargs.get("egk", [])
        erk = kwargs.get("erk", []) + ssrconfig["excludeRemarks"]
        self.__parser.filter_nodes(
            rs=rs, fk=fk, fgk=fgk, frk=frk, ek=ek, egk=egk, erk=erk
        )
        self.__parser.print_nodes()
        logger.info(f"{len(self.__parser.nodes)} node(s) will be tested.")

    def import_and_export(self, filename: str):
        self.__results = import_result(filename)
        self.__export_result(2)
        self.__results = []

    def __export_result(self, export_type: int = 0):
        er = ExportResult()
        er.set_time_used(self.__time_stamp_stop - self.__time_stamp_start)
        if self.test_mode == "TCP_PING":
            er.set_hide(ping=False, netflix=True, bilibili=True, StSpeed=True)
        elif self.test_mode == "STREAM":
            er.set_hide(stream=False, gping=True, StSpeed=True)
        elif self.test_mode == "ALL":
            er.set_hide(
                ntt=False,
                geoip=False,
                ping=False,
                stream=False,
                speed=False,
                port=False,
                multiplex=False,
            )
        elif self.test_mode == "WEB_PAGE_SIMULATION":
            er.export_wps_result(self.__results, export_type)
            return
        er.set_colors(self.colors)
        er.export(self.__results, export_type, self.sort_method)
