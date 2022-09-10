import logging
import time
from typing import Optional

from ssrspeed.config import ssrconfig
from ssrspeed.parsers import UniversalParser
from ssrspeed.result import ExportResult
from ssrspeed.result.importer import import_result
from ssrspeed.speedtest import SpeedTest
from ssrspeed.utils import sync_check_port

logger = logging.getLogger("Sub")

sync_check_port(ssrconfig["LOCAL_PORT"])


class SSRSpeedCore(object):
    def __init__(self):

        self.test_method: str = "ST_ASYNC"
        self.proxy_type: str = "SSR"
        self.web_mode: bool = False
        self.colors: str = "origin"
        self.sort_method: str = ""
        self.test_mode: str = "TCP_PING"

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
        result = []
        for node in nodes:
            result.append({"type": node.node_type, "config": node.config})
        return result

    def web_read_subscription(self, url: str) -> list:
        parser = UniversalParser()
        urls = url.split(" ")
        if parser:
            parser.read_subscription(urls)
            return self.__generate_web_configs(parser.nodes)
        return []

    def web_read_config_file(self, filename: str) -> list:
        parser = UniversalParser()
        if parser:
            parser.read_gui_config(filename)
            return self.__generate_web_configs(parser.nodes)
        return []

    def web_setup(self, **kwargs):
        self.test_method = kwargs.get("testMethod", "SOCKET")
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
            if cfg_filename:
                self.__parser.read_gui_config(cfg_filename)
            elif url:
                self.__parser.read_subscription(url.split(" "))
            else:
                raise ValueError("Subscription URL or configuration file must be set!")

    def start_test(self, use_ssr_csharp: bool = False):
        self.__time_stamp_start = time.time()
        self.__stc = SpeedTest(self.__parser, self.test_method, use_ssr_csharp)
        self.__status = "running"
        if self.test_mode == "TCP_PING":
            self.__stc.ping_only()
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
            if self.__stc:
                status = "running"
            else:
                status = "pending"
        else:
            status = self.__status
        r = {
            "status": status,
            "current": self.__stc.get_current()
            if (self.__stc and status == "running")
            else {},
            "results": self.__stc.get_result() if self.__stc else [],
        }
        return r

    def filter_nodes(
        self,
        fk: Optional[list] = None,
        fgk: Optional[list] = None,
        frk: Optional[list] = None,
        ek: Optional[list] = None,
        egk: Optional[list] = None,
        erk: Optional[list] = None,
    ):
        # 	self.__parser.excludeNode([], [], ssrconfig["excludeRemarks"])
        if not fk:
            fk = []
        if not fgk:
            fgk = []
        if not frk:
            frk = []
        if not ek:
            ek = []
        if not egk:
            egk = []
        if not erk:
            erk = []
        self.__parser.filter_nodes(
            fk, fgk, frk, ek, egk, erk + ssrconfig["excludeRemarks"]
        )
        self.__parser.print_nodes()
        logger.info(f"{len(self.__parser.nodes)} node(s) will be tested.")

    def import_and_export(self, filename: str, split: int = 0):
        self.__results = import_result(filename)
        self.__export_result(split, 2)
        self.__results = []

    def __export_result(self, split: int = 0, export_type: int = 0):
        er = ExportResult()
        er.set_time_used(self.__time_stamp_stop - self.__time_stamp_start)
        if self.test_mode == "WEB_PAGE_SIMULATION":
            er.export_wps_result(self.__results, export_type)
        else:
            er.set_colors(self.colors)
            er.export(self.__results, split, export_type, self.sort_method)
