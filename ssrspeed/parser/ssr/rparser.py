from typing import Optional

from ssrspeed.parser.bottom import BottomParser
from ssrspeed.parser.ssr import ParserShadowsocksR


class ShadowsocksRParser(BottomParser):
    def _parse_link(self, link: str) -> Optional[dict]:
        pssr = ParserShadowsocksR(self._get_shadowsocks_base_config())
        return pssr.parse_single_link(link)
