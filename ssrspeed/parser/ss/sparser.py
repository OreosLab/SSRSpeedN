import requests
from loguru import logger

from ssrspeed.parser.bottom import BottomParser
from ssrspeed.parser.ss import (
    ParserShadowsocksBasic,
    ParserShadowsocksClash,
    ParserShadowsocksD,
    ParserShadowsocksSIP002,
)
from ssrspeed.util import b64plus


class ShadowsocksParser(BottomParser):
    def _parse_link(self, link: str) -> dict:
        pssb = ParserShadowsocksBasic(self._get_shadowsocks_base_config())
        return pssb.parse_subs_config([link])[0]

    def read_subscription_config(self, url: str):
        header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
        }
        rep = requests.get(url, headers=header, timeout=15)
        rep.encoding = "utf-8"
        res = rep.content.decode("utf-8")
        if res[:6] == "ssd://":
            logger.info("Try ShadowsocksD Parser.")
            pssd = ParserShadowsocksD(self._get_shadowsocks_base_config())
            self._config_list = pssd.parse_subs_config(
                b64plus.decode(res[6:]).decode("utf-8")
            )
        else:
            try:
                logger.info("Try Shadowsocks Basic Parser.")
                links_arr = (b64plus.decode(res).decode("utf-8")).split("\n")
                try:
                    pssb = ParserShadowsocksBasic(self._get_shadowsocks_base_config())
                    self._config_list = pssb.parse_subs_config(links_arr)
                except ValueError:
                    logger.info("Try Shadowsocks SIP002 Parser.")
                    pssip002 = ParserShadowsocksSIP002(
                        self._get_shadowsocks_base_config()
                    )
                    self._config_list = pssip002.parse_subs_config(links_arr)
            except ValueError:
                logger.info("Try Shadowsocks Clash Parser.")
                pssc = ParserShadowsocksClash(self._get_shadowsocks_base_config())
                self._config_list = pssc.parse_subs_config(res)
        logger.info(f"Read {len(self._config_list)} node(s).")

    def read_gui_config(self, filename: str):
        logger.info("Try Shadowsocks Basic or ShadowsocksD Parser.")
        pssb = ParserShadowsocksBasic(self._get_shadowsocks_base_config())
        cfg = pssb.parse_gui_config(filename)
        if not cfg:
            logger.info("Not ShadowsocksBasic or ShadowsocksD Config.")
            logger.info("Try Shadowsocks Clash Parser.")
            pssc = ParserShadowsocksClash(self._get_shadowsocks_base_config())
            cfg = pssc.parse_gui_config(filename)
        if not cfg:
            logger.info("Not Clash Configs.")
            cfg = []
            logger.critical("Unsupported config file.")
        self._config_list = cfg
        logger.info(f"Read {len(self._config_list)} node(s).")
