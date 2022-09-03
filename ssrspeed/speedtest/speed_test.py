import asyncio
import copy
import logging
import os
import re
import socket
import time

import aiohttp
import pynat
import socks
from aiohttp_socks import ProxyConnector

from ssrspeed.config import ssrconfig
from ssrspeed.launchers import (
    ShadowsocksClient,
    ShadowsocksRClient,
    TrojanClient,
    V2RayClient,
)
from ssrspeed.speedtest.methodology import SpeedTestMethods
from ssrspeed.utils import check_port, domain2ip, ip_loc

logger = logging.getLogger("Sub")

LOCAL_ADDRESS = ssrconfig["localAddress"]
LOCAL_PORT = ssrconfig["localPort"]
PING_TEST = ssrconfig["ping"]
GOOGLE_PING_TEST = ssrconfig["gping"]
NETFLIX_TEST = ssrconfig["netflix"]
HBO_TEST = ssrconfig["hbo"]
DISNEY_TEST = ssrconfig["disney"]
YOUTUBE_TEST = ssrconfig["youtube"]
ABEMA_TEST = ssrconfig["abema"]
BAHAMUT_TEST = ssrconfig["bahamut"]
DAZN_TEST = ssrconfig["dazn"]
TVB_TEST = ssrconfig["tvb"]
BILIBILI_TEST = ssrconfig["bilibili"]
# Netflix requestIpAddress regex compile
nf_ip_re = re.compile(r'"requestIpAddress":"(.*)"')


class SpeedTest(object):
    def __init__(self, parser, method="SOCKET", use_ssr_cs=False):
        self.__configs = parser.nodes
        self.__use_ssr_cs = use_ssr_cs
        self.__test_method = method
        self.__results = []
        self.__current = {}
        self.__base_result = {
            "group": "N/A",
            "remarks": "N/A",
            "loss": 1,
            "ping": 0,
            "gPingLoss": 1,
            "gPing": 0,
            "dspeed": -1,
            "maxDSpeed": -1,
            "trafficUsed": 0,
            "geoIP": {
                "inbound": {"address": "N/A", "info": "N/A"},
                "outbound": {"address": "N/A", "info": "N/A"},
            },
            "rawSocketSpeed": [],
            "rawTcpPingStatus": [],
            "rawGooglePingStatus": [],
            "webPageSimulation": {"results": []},
            "ntt": {
                "type": "",
                "internal_ip": "",
                "internal_port": 0,
                "public_ip": "",
                "public_port": 0,
            },
            "Ntype": "None",
            "Htype": False,
            "Dtype": False,
            "Ytype": False,
            "Atype": False,
            "Btype": False,
            "Dztype": False,
            "Ttype": False,
            "Bltype": "N/A",
            "InRes": "N/A",
            "OutRes": "N/A",
            "InIP": "N/A",
            "OutIP": "N/A",
            "port": 0,
        }

    def __get_base_result(self):
        return copy.deepcopy(self.__base_result)

    def __get_next_config(self):
        try:
            return self.__configs.pop(0)
        except IndexError:
            return None

    def __get_client(self, client_type: str):
        if client_type == "Shadowsocks":
            return ShadowsocksClient()
        elif client_type == "ShadowsocksR":
            client = ShadowsocksRClient()
            if self.__use_ssr_cs:
                client.useSsrCSharp = True
            return client
        elif client_type == "Trojan":
            return TrojanClient()
        elif client_type == "V2Ray":
            return V2RayClient()
        else:
            return None

    def reset_status(self):
        self.__results = []
        self.__current = {}

    def get_result(self):
        return self.__results

    def get_current(self):
        return self.__current

    def __geo_ip_inbound(self, config):
        inbound_ip = domain2ip(config["server"])
        self.inboundGeoIP = inbound_ip
        inbound_info = ip_loc(inbound_ip)
        inbound_geo = (
            f"{inbound_info.get('country', 'N/A')} {inbound_info.get('city', 'Unknown City')}, "
            f"{inbound_info.get('organization', 'N/A')}"
        )
        self.inboundGeoRES = f"{inbound_info.get('city', 'Unknown City')}, {inbound_info.get('organization', 'N/A')}"
        logger.info(f"Node inbound IP : {inbound_ip}, Geo : {inbound_geo}")
        return inbound_ip, inbound_geo, inbound_info.get("country_code", "N/A")

    async def __geo_ip_outbound(self, attrs):
        outbound_info = ip_loc()
        self.outbound_ip = outbound_info.get("ip", "N/A")
        self.outboundGeoIP = self.outbound_ip
        outbound_geo = (
            f"{outbound_info.get('country', 'N/A')} {outbound_info.get('city', 'Unknown City')}, "
            f"{outbound_info.get('organization', 'N/A')}"
        )
        self.outboundGeoRES = f"{outbound_info.get('country_code', 'N/A')}, {outbound_info.get('organization', 'N/A')}"
        logger.info(f"Node outbound IP : {self.outbound_ip}, Geo : {outbound_geo}")
        host = "127.0.0.1"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/64.0.3282.119 Safari/537.36 ",
        }
        test_list = []
        if self.outbound_ip != "N/A":
            if NETFLIX_TEST:
                test_list.append(
                    asyncio.create_task(
                        SpeedTest.netflix(host, headers, attrs, self.outbound_ip)
                    )
                )
            if HBO_TEST:
                test_list.append(
                    asyncio.create_task(SpeedTest.hbomax(host, headers, attrs))
                )
            if DISNEY_TEST:
                test_list.append(
                    asyncio.create_task(SpeedTest.disneyplus(host, headers, attrs))
                )
            if YOUTUBE_TEST:
                test_list.append(
                    asyncio.create_task(SpeedTest.youtube(host, headers, attrs))
                )
            if ABEMA_TEST:
                test_list.append(
                    asyncio.create_task(SpeedTest.abema(host, headers, attrs))
                )
            if BAHAMUT_TEST:
                test_list.append(
                    asyncio.create_task(SpeedTest.gamer(host, headers, attrs))
                )
            if DAZN_TEST:
                test_list.append(
                    asyncio.create_task(SpeedTest.indazn(host, headers, attrs))
                )
            if TVB_TEST:
                test_list.append(
                    asyncio.create_task(SpeedTest.mytvsuper(host, headers, attrs))
                )
            if BILIBILI_TEST:
                test_list.append(
                    asyncio.create_task(SpeedTest.bilibili(host, headers, attrs))
                )
            await asyncio.wait(test_list)
        return self.outbound_ip, outbound_geo, outbound_info.get("country_code", "N/A")

    def __tcp_ping(self, server, port):
        latency_test = None
        res = {
            "loss": self.__base_result["loss"],
            "ping": self.__base_result["ping"],
            "rawTcpPingStatus": self.__base_result["rawTcpPingStatus"],
            "gPing": self.__base_result["gPing"],
            "gPingLoss": self.__base_result["gPingLoss"],
            "rawGooglePingStatus": self.__base_result["rawGooglePingStatus"],
        }

        if PING_TEST:
            st = SpeedTestMethods()
            latency_test = st.tcp_ping(server, port)
            res["loss"] = 1 - latency_test[1]
            res["ping"] = latency_test[0]
            res["rawTcpPingStatus"] = latency_test[2]
            logger.debug(latency_test)
            time.sleep(1)

        if (not PING_TEST) or (latency_test[0] > 0):
            if GOOGLE_PING_TEST:
                try:
                    st = SpeedTestMethods()
                    google_ping_test = st.google_ping()
                    res["gPing"] = google_ping_test[0]
                    res["gPingLoss"] = 1 - google_ping_test[1]
                    res["rawGooglePingStatus"] = google_ping_test[2]
                except Exception:
                    logger.exception("")
                    pass
        return res

    @classmethod
    def __nat_type_test(cls):
        s = socks.socksocket(type=socket.SOCK_DGRAM)
        s.set_proxy(socks.PROXY_TYPE_SOCKS5, LOCAL_ADDRESS, LOCAL_PORT)
        sport = ssrconfig["ntt"]["internal_port"]
        try:
            logger.info("Performing UDP NAT Type Test.")
            t, eip, eport, sip = pynat.get_ip_info(
                source_ip=ssrconfig["ntt"]["internal_ip"],
                source_port=sport,
                include_internal=True,
                sock=s,
            )
            return t, eip, eport, sip, sport
        except Exception:
            logger.exception("\n")
            return None, None, None, None, None
        finally:
            s.close()

    def __start_test(self, test_mode="FULL"):
        _item = None
        client = None
        done_nodes = 0
        total_nodes = len(self.__configs)
        node = self.__get_next_config()
        self.__results = []
        while node:
            done_nodes += 1
            try:
                cfg = node.config
                logger.info(
                    f"Starting test {cfg['group']} - {cfg['remarks']} [{done_nodes}/{total_nodes}]"
                )
                client = self.__get_client(node.node_type)
                if not client:
                    logger.warning(f"Unknown Node Type: {node.node_type}.")
                    node = self.__get_next_config()
                    continue
                _item = self.__get_base_result()
                _item["group"] = cfg["group"]
                _item["remarks"] = cfg["remarks"]
                self.__current = _item
                cfg["server_port"] = int(cfg["server_port"])
                _item["port"] = cfg["server_port"]
                client.start_client(cfg)

                # Check clients started
                time.sleep(1)
                ct = 0
                client_started = True
                while not client.check_alive():
                    ct += 1
                    if ct > 3:
                        client_started = False
                        break
                    client.start_client(cfg)
                    time.sleep(1)
                if not client_started:
                    logger.error("Failed to start clients.")
                    continue
                logger.info("Client started.")

                # Check port
                ct = 0
                port_opened = True
                while True:
                    if ct >= 3:
                        port_opened = False
                        break
                    time.sleep(1)
                    try:
                        check_port(LOCAL_PORT)
                        break
                    except socket.timeout:
                        ct += 1
                        logger.error(f"Port {LOCAL_PORT} timeout.")
                    except ConnectionRefusedError:
                        ct += 1
                        logger.error(f"Connection refused on port {LOCAL_PORT}.")
                    except Exception:
                        ct += 1
                        logger.exception("An error occurred:\n")
                if not port_opened:
                    logger.error(f"Port {LOCAL_PORT} closed.")
                    continue

                inbound_info = self.__geo_ip_inbound(cfg)
                _item["geoIP"]["inbound"]["address"] = inbound_info[0]
                _item["geoIP"]["inbound"]["info"] = inbound_info[1]
                ping_result = self.__tcp_ping(cfg["server"], cfg["server_port"])
                if isinstance(ping_result, dict):
                    for k in ping_result.keys():
                        _item[k] = ping_result[k]
                if os.name == "nt":
                    asyncio.set_event_loop_policy(
                        asyncio.WindowsSelectorEventLoopPolicy()
                    )
                loop = asyncio.new_event_loop()
                outbound_info = loop.run_until_complete(self.__geo_ip_outbound(_item))
                _item["geoIP"]["outbound"]["address"] = outbound_info[0]
                _item["geoIP"]["outbound"]["info"] = outbound_info[1]

                if (
                    (not GOOGLE_PING_TEST)
                    or _item["gPing"] > 0
                    or outbound_info[2] == "CN"
                ):
                    nat_info = ""
                    st = SpeedTestMethods()
                    if test_mode == "WPS":
                        res = st.start_wps_test()
                        _item["webPageSimulation"]["results"] = res
                        logger.info(
                            f"[{_item['group']}] - [{_item['remarks']}] "
                            f"- Loss: [{(_item['loss'] * 100):.2f}%] "
                            f"- TCP Ping: [{int(_item['ping'] * 1000):.2f}] "
                            f"- Google Loss: [{(_item['gPingLoss'] * 100):.2f}%] "
                            f"- Google Ping: [{(int(_item['gPing'] * 1000)):.2f}] "
                            f"- [WebPageSimulation]"
                        )
                    else:
                        if ssrconfig["ntt"]["enabled"]:
                            t, eip, eport, sip, sport = SpeedTest.__nat_type_test()
                            _item["ntt"]["type"] = t
                            _item["ntt"]["internal_ip"] = sip
                            _item["ntt"]["internal_port"] = sport
                            _item["ntt"]["public_ip"] = eip
                            _item["ntt"]["public_port"] = eport
                            if t:
                                nat_info += " - NAT Type: " + t
                                if t != pynat.BLOCKED:
                                    nat_info += f" - Internal End: {sip}:{sport}"
                                    nat_info += f" - Public End: {eip}:{eport}"
                        if test_mode == "PING":
                            logger.info(
                                f"[{_item['group']}] - [{_item['remarks']}] "
                                f"- Loss: [{(_item['loss'] * 100):.2f}%] "
                                f"- TCP Ping: [{int(_item['ping'] * 1000):.2f}] "
                                f"- Google Loss: [{(_item['gPingLoss'] * 100):.2f}%] "
                                f"- Google Ping: [{int(_item['gPing'] * 1000):.2f}]"
                                f"{nat_info}"
                            )
                        elif test_mode == "FULL":
                            test_res = st.start_test(self.__test_method)
                            if int(test_res[0]) == 0:
                                logger.warning("Re-testing node.")
                                test_res = st.start_test(self.__test_method)
                            _item["dspeed"] = test_res[0]
                            _item["maxDSpeed"] = test_res[1]
                            _item["InRes"] = self.inboundGeoRES
                            _item["OutRes"] = self.outboundGeoRES
                            _item["InIP"] = self.inboundGeoIP
                            _item["OutIP"] = self.outboundGeoIP
                            try:
                                _item["trafficUsed"] = test_res[3]
                                _item["rawSocketSpeed"] = test_res[2]
                            except Exception:
                                pass

                            logger.info(
                                f"[{_item['group']}] - [{_item['remarks']}] "
                                f"- Loss: [{(_item['loss'] * 100):.2f}%] "
                                f"- TCP Ping: [{int(_item['ping'] * 1000):.2f}] "
                                f"- Google Loss: [{(_item['gPingLoss'] * 100):.2f}%] "
                                f"- Google Ping: [{int(_item['gPing'] * 1000):.2f}] "
                                f"- AvgStSpeed: [{(_item['dspeed'] / 1024 / 1024):.2f}MB/s] "
                                f"- AvgMtSpeed: [{(_item['maxDSpeed'] / 1024 / 1024):.2f}MB/s]"
                                f"{nat_info}"
                            )
                        else:
                            logger.error(f"Unknown Test Mode {test_mode}.")
            except Exception:
                logger.exception("\n")
            finally:
                self.__results.append(_item)
                if client:
                    client.stop_client()
                node = self.__get_next_config()
                time.sleep(1)

        self.__current = {}

    def web_page_simulation(self):
        logger.info("Test mode : Web Page Simulation")
        self.__start_test("WPS")

    def tcping_only(self):
        logger.info("Test mode : tcp ping only")
        self.__start_test("PING")

    def full_test(self):
        logger.info(
            f"Test mode : speed and tcp ping. Test method : {self.__test_method}"
        )
        self.__start_test()

    @classmethod
    async def netflix(cls, host, headers, attrs, outbound_ip):
        logger.info(f"Performing netflix test LOCAL_PORT: {LOCAL_PORT}.")
        try:
            sum_ = 0
            async with aiohttp.ClientSession(
                headers=headers,
                connector=ProxyConnector(host=host, port=LOCAL_PORT),
                timeout=aiohttp.ClientTimeout(connect=10),
            ) as session:
                async with session.get(
                    url="https://www.netflix.com/title/70242311"
                ) as response1:
                    if response1.status == 200:
                        sum_ += 1
                        netflix_ip = nf_ip_re.findall(str(await response1.read()))[0].split(",")[0]
                        logger.info("Netflix IP : " + netflix_ip)
                    async with session.get(
                        url="https://www.netflix.com/title/70143836"
                    ) as response2:
                        rg = ""
                        if response2.status == 200:
                            sum_ += 1
                            rg = (
                                "("
                                + str(response2.url).split("com/")[1].split("/")[0]
                                + ")"
                            )
                        if rg == "(title)":
                            rg = "(us)"
                        # 测试连接状态
                        if sum_ == 0:
                            logger.info("Netflix test result: None.")
                            attrs["Ntype"] = "None"
                        elif sum_ == 1:
                            logger.info("Netflix test result: Only Original.")
                            attrs["Ntype"] = "Only Original"
                        elif outbound_ip == netflix_ip:
                            logger.info("Netflix test result: Full Native.")
                            attrs["Ntype"] = "Full Native" + rg
                        else:
                            logger.info("Netflix test result: Full DNS.")
                            attrs["Ntype"] = "Full DNS" + rg
        except Exception as e:
            logger.error("代理服务器连接异常：" + str(e.args))

    @classmethod
    async def hbomax(cls, host, headers, attrs):
        logger.info(f"Performing HBO max test LOCAL_PORT: {LOCAL_PORT}.")
        try:
            async with aiohttp.ClientSession(
                headers=headers,
                connector=ProxyConnector(host=host, port=LOCAL_PORT),
                timeout=aiohttp.ClientTimeout(connect=10),
            ) as session:
                async with session.get(
                    url="https://www.hbomax.com/", allow_redirects=False
                ) as response:
                    if response.status == 200:
                        attrs["Htype"] = True
                    else:
                        attrs["Htype"] = False
        except Exception as e:
            logger.error("代理服务器连接异常：" + str(e.args))

    @classmethod
    async def disneyplus(cls, host, headers, attrs):
        logger.info(f"Performing Disney plus test LOCAL_PORT: {LOCAL_PORT}.")
        try:
            async with aiohttp.ClientSession(
                headers=headers,
                connector=ProxyConnector(host=host, port=LOCAL_PORT),
                timeout=aiohttp.ClientTimeout(connect=5),
            ) as session:
                async with session.get(
                    url="https://www.disneyplus.com/"
                ) as response1, session.get(
                    url="https://global.edge.bamgrid.com/token"
                ) as response2:
                    if response1.status == 200 and response2.status != 403:
                        text = await response1.text()
                        if text.find("Region", 0, 400) == -1:
                            attrs["Dtype"] = False
                        elif response1.history:
                            if 300 <= response1.history[0].status <= 399:
                                attrs["Dtype"] = False
                        else:
                            attrs["Dtype"] = True
                    else:
                        attrs["Dtype"] = False
        except Exception as e:
            logger.error("代理服务器连接异常：" + str(e.args))

    @classmethod
    async def youtube(cls, host, headers, attrs):
        logger.info(f"Performing Youtube Premium test LOCAL_PORT: {LOCAL_PORT}.")
        try:
            async with aiohttp.ClientSession(
                headers=headers,
                connector=ProxyConnector(host=host, port=LOCAL_PORT),
                timeout=aiohttp.ClientTimeout(connect=10),
            ) as session:
                async with session.get(
                    url="https://music.youtube.com/", allow_redirects=False
                ) as response:
                    if "is not available" in await response.text():
                        attrs["Ytype"] = False
                    elif response.status == 200:
                        attrs["Ytype"] = True
                    else:
                        attrs["Ytype"] = False
        except Exception as e:
            logger.error("代理服务器连接异常：" + str(e.args))

    @classmethod
    async def abema(cls, host, headers, attrs):
        logger.info(f"Performing Abema test LOCAL_PORT: {LOCAL_PORT}.")
        try:
            async with aiohttp.ClientSession(
                headers=headers,
                connector=ProxyConnector(host=host, port=LOCAL_PORT),
                timeout=aiohttp.ClientTimeout(connect=10),
            ) as session:
                async with session.get(
                    url="https://api.abema.io/v1/ip/check?device=android",
                    allow_redirects=False,
                ) as response:
                    text = await response.text()
                    if text.count("Country") > 0:
                        attrs["Atype"] = True
                    else:
                        attrs["Atype"] = False
        except Exception as e:
            logger.error("代理服务器连接异常：" + str(e.args))

    @classmethod
    async def gamer(cls, host, headers, attrs):
        logger.info(f"Performing Bahamut test LOCAL_PORT: {LOCAL_PORT}.")
        try:
            async with aiohttp.ClientSession(
                headers=headers,
                connector=ProxyConnector(host=host, port=LOCAL_PORT),
                timeout=aiohttp.ClientTimeout(connect=10),
            ) as session:
                async with session.get(
                    url="https://ani.gamer.com.tw/ajax/token.php?adID=89422&sn=14667",
                    allow_redirects=False,
                ) as response:
                    text = await response.text()
                    if text.count("animeSn") > 0:
                        attrs["Btype"] = True
                    else:
                        attrs["Btype"] = False
        except Exception as e:
            logger.error("代理服务器连接异常：" + str(e.args))

    @classmethod
    async def indazn(cls, host, headers, attrs):
        logger.info(f"Performing Dazn test LOCAL_PORT: {LOCAL_PORT}.")
        try:
            async with aiohttp.ClientSession(
                headers=headers,
                connector=ProxyConnector(host=host, port=LOCAL_PORT, verify_ssl=False),
                timeout=aiohttp.ClientTimeout(connect=10),
            ) as session:
                payload = {
                    "LandingPageKey": "generic",
                    "Languages": "zh-CN,zh,en",
                    "Platform": "web",
                    "PlatformAttributes": {},
                    "Manufacturer": "",
                    "PromoCode": "",
                    "Version": "2",
                }
                async with session.post(
                    url="https://startup.core.indazn.com/misl/v5/Startup",
                    json=payload,
                    allow_redirects=False,
                ) as response:
                    if response.status == 200:
                        attrs["Dztype"] = True
                    else:
                        attrs["Dztype"] = False
        except Exception as e:
            logger.error("代理服务器连接异常：" + str(e.args))

    @classmethod
    async def mytvsuper(cls, host, headers, attrs):
        logger.info(f"Performing TVB test LOCAL_PORT: {LOCAL_PORT}.")
        try:
            async with aiohttp.ClientSession(
                headers=headers,
                connector=ProxyConnector(host=host, port=LOCAL_PORT),
                timeout=aiohttp.ClientTimeout(connect=10),
            ) as session:
                async with session.get(
                    url="https://www.mytvsuper.com/iptest.php", allow_redirects=False
                ) as response:
                    text = await response.text()
                    if text.count("HK") > 0:
                        attrs["Ttype"] = True
                    else:
                        attrs["Ttype"] = False
        except Exception as e:
            logger.error("代理服务器连接异常：" + str(e.args))

    @classmethod
    async def bilibili(cls, host, headers, attrs):
        logger.info(f"Performing Bilibili test LOCAL_PORT: {LOCAL_PORT}.")
        try:
            async with aiohttp.ClientSession(
                headers=headers,
                connector=ProxyConnector(host=host, port=LOCAL_PORT),
                timeout=aiohttp.ClientTimeout(connect=10),
            ) as session:
                params = {
                    "avid": 50762638,
                    "cid": 100279344,
                    "qn": 0,
                    "type": "",
                    "otype": "json",
                    "ep_id": 268176,
                    "fourk": 1,
                    "fnver": 0,
                    "fnval": 16,
                    "module": "bangumi",
                }
                async with session.get(
                    url="https://api.bilibili.com/pgc/player/web/playurl",
                    params=params,
                    allow_redirects=False,
                ) as response:
                    if response.status == 200:
                        json_data = await response.json()
                        if json_data["code"] == 0:
                            attrs["Bltype"] = "台湾"
                        else:
                            params = {
                                "avid": 18281381,
                                "cid": 29892777,
                                "qn": 0,
                                "type": "",
                                "otype": "json",
                                "ep_id": 183799,
                                "fourk": 1,
                                "fnver": 0,
                                "fnval": 16,
                                "module": "bangumi",
                            }
                            session.cookie_jar.clear()
                            async with session.get(
                                url="https://api.bilibili.com/pgc/player/web/playurl",
                                params=params,
                                allow_redirects=False,
                            ) as response2:
                                if response2.status == 200:
                                    json_data2 = await response2.json()
                                    if json_data2["code"] == 0:
                                        attrs["Bltype"] = "港澳台"
                                else:
                                    attrs["Bltype"] = "N/A"
        except Exception as e:
            logger.error("代理服务器连接异常：" + str(e.args))
