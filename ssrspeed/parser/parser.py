import contextlib
import json
import os
from copy import deepcopy
from typing import List, Optional, Union

import requests
from loguru import logger

from ssrspeed.config import ssrconfig
from ssrspeed.parser.clash import ClashParser
from ssrspeed.parser.conf import V2RayBaseConfigs, shadowsocks_get_config
from ssrspeed.parser.filter import NodeFilter
from ssrspeed.parser.ss import (
    ParserShadowsocksBasic,
    ParserShadowsocksD,
    ParserShadowsocksSIP002,
)
from ssrspeed.parser.ssr import ParserShadowsocksR
from ssrspeed.parser.trojan import TrojanParser
from ssrspeed.parser.v2ray import ParserV2RayN, ParserV2RayQuantumult
from ssrspeed.type.node import NodeShadowsocks, NodeShadowsocksR, NodeTrojan, NodeV2Ray
from ssrspeed.util import b64plus

PROXY_SETTINGS = ssrconfig["proxy"]
LOCAL_ADDRESS = ssrconfig["localAddress"]
LOCAL_PORT = ssrconfig["localPort"]
TIMEOUT = 10

TMP_DIR = ssrconfig["path"]["tmp"]
if not os.path.exists(TMP_DIR):
    os.makedirs(TMP_DIR)
TEST_TXT = f"{TMP_DIR}test.txt"


class UniversalParser:
    def __init__(self):
        self.__nodes: list = []
        self.__ss_base_cfg: dict = shadowsocks_get_config(
            LOCAL_ADDRESS, LOCAL_PORT, TIMEOUT
        )

    @staticmethod
    def web_config_to_node(
        configs: List[dict],
    ) -> List[
        Union[
            Optional[NodeShadowsocks], Optional[NodeShadowsocksR], Optional[NodeV2Ray],
        ]
    ]:
        result: list = []
        for _config in configs:
            _type = _config.get("type", "N/A")
            if _type == "Shadowsocks":
                result.append(NodeShadowsocks(_config["config"]))
            elif _type == "ShadowsocksR":
                result.append(NodeShadowsocksR(_config["config"]))
            elif _type == "V2Ray":
                result.append(NodeV2Ray(_config["config"]))
            elif _type == "Trojan":
                result.append(NodeTrojan(_config["config"]))
            else:
                logger.warning(f"Unknown node type: {_type}")
        return result

    @property
    def nodes(self) -> list:
        return deepcopy(self.__nodes)

    def __get_ss_base_config(self) -> dict:
        return deepcopy(self.__ss_base_cfg)

    def __clean_nodes(self):
        self.__nodes.clear()

    def set_nodes(self, nodes: list):
        self.__clean_nodes()
        self.__nodes = nodes

    def set_group(self, group: str):
        tmp_nodes = deepcopy(self.__nodes)
        self.__clean_nodes()
        for node in tmp_nodes:
            if group:
                node.update_config({"group": group})
            self.__nodes.append(node)

    def parse_links(
        self, links: list
    ) -> List[
        Union[
            Optional[NodeShadowsocks],
            Optional[NodeShadowsocksR],
            Optional[NodeV2Ray],
            Optional[NodeTrojan],
        ]
    ]:
        # Single link parse
        result: list = []
        for link in links:
            link = link.replace("\r", "")
            node: Union[
                Optional[NodeShadowsocks],
                Optional[NodeShadowsocksR],
                Optional[NodeV2Ray],
                Optional[NodeTrojan],
            ] = None

            if link[:5] == "ss://":
                # Shadowsocks
                cfg = None
                try:
                    pssb = ParserShadowsocksBasic(self.__get_ss_base_config())
                    cfg = pssb.parse_single_link(link)
                except ValueError:
                    pssip002 = ParserShadowsocksSIP002(self.__get_ss_base_config())
                    cfg = pssip002.parse_single_link(link)
                if cfg:
                    node = NodeShadowsocks(cfg)
                else:
                    logger.warning(f"Invalid shadowsocks link {link}")

            elif link[:6] == "ssr://":
                # ShadowsocksR
                pssr = ParserShadowsocksR(self.__get_ss_base_config())
                if cfg := pssr.parse_single_link(link):
                    node = NodeShadowsocksR(cfg)
                else:
                    logger.warning(f"Invalid shadowsocksR link {link}")

            elif link[:8] == "vmess://":
                # Vmess link (V2RayN and Quan)
                # V2RayN Parser
                cfg = None
                logger.info("Try V2RayN Parser.")
                pv2rn = ParserV2RayN()
                with contextlib.suppress(ValueError):
                    cfg = pv2rn.parse_subs_config(link)
                if not cfg:
                    # Quantumult Parser
                    logger.info("Try Quantumult Parser.")
                    pq = ParserV2RayQuantumult()
                    with contextlib.suppress(ValueError):
                        cfg = pq.parse_subs_config(link)
                if not cfg:
                    logger.error(f"Invalid vmess link: {link}")
                else:
                    gen_cfg = V2RayBaseConfigs.generate_config(
                        cfg, LOCAL_ADDRESS, LOCAL_PORT
                    )
                    node = NodeV2Ray(gen_cfg)

            elif link[:9] == "trojan://":
                cfg = None
                logger.info("Try Trojan Parser.")
                ptrojan = TrojanParser()
                with contextlib.suppress(ValueError):
                    cfg = ptrojan.parse_single_link(link)
                if cfg:
                    node = NodeTrojan(cfg)

            else:
                logger.warning(f"Unsupported link: {link}")

            if node:
                result.append(node)

        return result

    @staticmethod
    def __parse_clash(clash_cfg: str) -> list:
        result: list = []
        pc = ClashParser(shadowsocks_get_config(LOCAL_ADDRESS, LOCAL_PORT, TIMEOUT))
        pc.parse_config(clash_cfg)
        cfgs = pc.config_list
        for cfg in cfgs:
            if cfg["type"] == "ss":
                result.append(NodeShadowsocks(cfg["config"]))
            elif cfg["type"] == "vmess":
                result.append(
                    NodeV2Ray(
                        V2RayBaseConfigs.generate_config(
                            cfg["config"], LOCAL_ADDRESS, LOCAL_PORT
                        )
                    )
                )
            elif cfg["type"] == "trojan":
                result.append(NodeTrojan(cfg["config"]))

        return result

    def filter_nodes(self, **kwargs):
        rs = kwargs.get("rs", False)
        fk = kwargs.get("fk", [])
        fgk = kwargs.get("fgk", [])
        frk = kwargs.get("frk", [])
        ek = kwargs.get("ek", [])
        egk = kwargs.get("egk", [])
        erk = kwargs.get("erk", [])
        nf = NodeFilter()
        self.__nodes = nf.filter_node(
            self.__nodes, rs=rs, fk=fk, fgk=fgk, frk=frk, ek=ek, egk=egk, erk=erk
        )

    def print_nodes(self):
        for item in self.nodes:
            logger.info(f'{item.config["group"]} - {item.config["remarks"]}')

    def read_subscription(self, urls: list):
        for url in urls:
            if not url:
                continue

            if (
                url.startswith("ss://")
                or url.startswith("ssr://")
                or url.startswith("vmess://")
                or url.startswith("trojan://")
            ):
                self.__nodes.extend(self.parse_links([url]))
                continue

            logger.info(f"Reading {url}")
            header = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
            }
            clash_ua = {"User-Agent": "Clash"}

            try:
                r = requests.get(url, headers=clash_ua, timeout=15)
                t = r.headers["subscription-userinfo"]
                dl = int(t[t.find("download") + 9 : t.find("total") - 2])
                _sum = dl
            except Exception:
                _sum = 0

            with open(TEST_TXT, "a+", encoding="utf-8") as test:
                test.write(f"{url}\n")
                test.write(f"{_sum}\n")

            if PROXY_SETTINGS["enabled"]:
                auth = ""
                if PROXY_SETTINGS["username"]:
                    auth = f'{PROXY_SETTINGS["username"]}:{PROXY_SETTINGS["password"]}@'
                proxy = f'socks5://{auth}{PROXY_SETTINGS["address"]}:{PROXY_SETTINGS["port"]}'
                proxies = {"http": proxy, "https": proxy}
                logger.info(f"Reading subscription via {proxy}")
                rep = requests.get(url, headers=header, timeout=15, proxies=proxies)
            else:
                rep = requests.get(url, headers=header, timeout=15)
            rep.encoding = "utf-8"
            res = rep.text

            parsed = False
            # Try ShadowsocksD Parser
            if res[:6] == "ssd://":
                parsed = True
                logger.info("Try ShadowsocksD Parser.")
                pssd = ParserShadowsocksD(
                    shadowsocks_get_config(LOCAL_ADDRESS, LOCAL_PORT, TIMEOUT)
                )
                cfgs = pssd.parse_subs_config(b64plus.decode(res[6:]).decode("utf-8"))
                for cfg in cfgs:
                    self.__nodes.append(NodeShadowsocks(cfg))
            if parsed:
                continue

            # Try base64 decode
            try:
                res = res.strip()
                links = (b64plus.decode(res).decode("utf-8")).split("\n")
                logger.debug("Base64 decode success.")
                self.__nodes.extend(self.parse_links(links))
                parsed = True
            except ValueError:
                logger.info("Base64 decode failed.")
            if parsed:
                continue

            # Try Clash Parser
            self.__nodes.extend(self.__parse_clash(res))

    def read_gui_config(self, filename: str):
        with open(filename, "r", encoding="utf-8") as f:
            raw_data = f.read()
        try:
            # Try Load as Json
            data = json.loads(raw_data)
            # Identification of proxy type
            # Shadowsocks(D)
            if (
                "subscriptions" in data
                or "serverSubscribes" not in data
                and "vmess" not in data
            ):
                pssb = ParserShadowsocksBasic(self.__get_ss_base_config())
                for cfg in pssb.parse_gui_data(data):
                    self.__nodes.append(NodeShadowsocks(cfg))
            # ShadowsocksR
            elif "serverSubscribes" in data:
                pssr = ParserShadowsocksR(self.__get_ss_base_config())
                for cfg in pssr.parse_gui_data(data):
                    self.__nodes.append(NodeShadowsocksR(cfg))
            # V2RayN
            else:
                pv2n = ParserV2RayN()
                cfgs = pv2n.parse_gui_data(data)
                for cfg in cfgs:
                    self.__nodes.append(
                        NodeV2Ray(
                            V2RayBaseConfigs.generate_config(
                                cfg, LOCAL_ADDRESS, LOCAL_PORT
                            )
                        )
                    )
        except json.JSONDecodeError:
            # Try Load as Yaml
            self.__nodes = self.__parse_clash(raw_data)
