import requests
from loguru import logger

from ssrspeed.parser.bottom import BottomParser
from ssrspeed.parser.conf import V2RayBaseConfigs
from ssrspeed.parser.v2ray import ParserV2RayClash, ParserV2RayN, ParserV2RayQuantumult
from ssrspeed.util import b64plus


class V2RayParser(V2RayBaseConfigs, BottomParser):
    def __generate_config(self, config: dict) -> dict:
        return super().generate_config(
            config, self._get_local_config()[0], self._get_local_config()[1]
        )

    def _parse_link(self, link: str) -> dict:
        if link[:8] != "vmess://":
            logger.error(f"Unsupported link : {link}")
            return {}
        pv2rn = ParserV2RayN()
        cfg = pv2rn.parse_subs_config(link)
        if not cfg:
            pq = ParserV2RayQuantumult()
            cfg = pq.parse_subs_config(link)
        if not cfg:
            logger.error(f"Parse link {link} failed.")
            return {}
        return self.__generate_config(cfg)

    def read_subscription_config(self, url: str):
        header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
        }
        rep = requests.get(url, headers=header, timeout=15)
        rep.encoding = "utf-8"
        res = rep.content.decode("utf-8")
        try:
            links_arr = (b64plus.decode(res).decode("utf-8")).split("\n")
            for link in links_arr:
                link = link.strip()
                if cfg := self._parse_link(link):
                    self._config_list.append(cfg)
        except ValueError:
            logger.info("Try V2Ray Clash Parser.")
            pv2rc = ParserV2RayClash()
            for cfg in pv2rc.parse_subs_config(res):
                self._config_list.append(self.__generate_config(cfg))
        logger.info(f"Read {len(self._config_list)} node(s).")

    def read_gui_config(self, filename):
        pv2rc = ParserV2RayClash()
        v2rnp = ParserV2RayN()
        raw_gui_configs = v2rnp.parse_gui_config(filename)
        if raw_gui_configs is False:
            logger.info("Not V2RayN Config.")
            raw_gui_configs = pv2rc.parse_gui_config(filename)
        if raw_gui_configs is False:
            logger.info("Not Clash Config.")
            logger.critical("Gui config parse failed.")
            raw_gui_configs = []
        for _dict in raw_gui_configs:
            _cfg = self.__generate_config(_dict)
            self._config_list.append(_cfg)
        logger.info(f"Read {len(self._config_list)} node(s).")
