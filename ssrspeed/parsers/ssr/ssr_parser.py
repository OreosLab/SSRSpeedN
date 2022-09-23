from typing import Optional

from ssrspeed.parsers.base import BaseParser
from ssrspeed.parsers.ssr import ParserShadowsocksR


class ShadowsocksRParser(BaseParser):
    def _parse_link(self, link: str) -> Optional[dict]:
        pssr = ParserShadowsocksR(self._get_shadowsocks_base_config())
        return pssr.parse_single_link(link)
