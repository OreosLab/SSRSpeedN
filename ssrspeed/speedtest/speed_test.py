import copy
import logging
import socket
import time

import pynat
import requests
import socks
from bs4 import BeautifulSoup

from ssrspeed.config import ssrconfig
from ssrspeed.launchers import ShadowsocksClient, ShadowsocksRClient, V2RayClient
from ssrspeed.speedtest.methodology import SpeedTestMethods
from ssrspeed.utils import check_port, domain2ip, ip_loc

logger = logging.getLogger("Sub")

LOCAL_ADDRESS = ssrconfig["localAddress"]
LOCAL_PORT = ssrconfig["localPort"]
PING_TEST = ssrconfig["ping"]
GOOGLE_PING_TEST = ssrconfig["gping"]
NETFLIX_TEXT = ssrconfig["netflix"]
HBO_TEXT = ssrconfig["hbo"]
DISNEY_TEXT = ssrconfig["disney"]
YOUTUBE_TEXT = ssrconfig["youtube"]
TVB_TEXT = ssrconfig["tvb"]
ABEMA_TEXT = ssrconfig["abema"]
BAHAMUT_TEXT = ssrconfig["bahamut"]
ntype = "None"
htype = False
dtype = False
ytype = False
ttype = False
atype = False
btype = False
inboundGeoRES = ""
outboundGeoRES = ""
inboundGeoIP = ""
outboundGeoIP = ""


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
            "Ntype": "N/A",
            "Htype": False,
            "Dtype": False,
            "Ytype": False,
            "Ttype": False,
            "Atype": False,
            "Btype": False,
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

    @staticmethod
    def __geo_ip_inbound(config):
        inbound_ip = domain2ip(config["server"])
        global inboundGeoIP
        inboundGeoIP = inbound_ip
        inbound_info = ip_loc(inbound_ip)
        inbound_geo = "{} {}, {}".format(
            inbound_info.get("country", "N/A"),
            inbound_info.get("city", "Unknown City"),
            inbound_info.get("organization", "N/A"),
        )
        global inboundGeoRES
        inboundGeoRES = "{}, {}".format(
            inbound_info.get("city", "Unknown City"),
            inbound_info.get("organization", "N/A"),
        )
        logger.info("Node inbound IP : {}, Geo : {}".format(inbound_ip, inbound_geo))
        return inbound_ip, inbound_geo, inbound_info.get("country_code", "N/A")

    @staticmethod
    def __geo_ip_outbound():
        outbound_info = ip_loc()
        outbound_ip = outbound_info.get("ip", "N/A")
        global outboundGeoIP
        outboundGeoIP = outbound_ip
        outbound_geo = "{} {}, {}".format(
            outbound_info.get("country", "N/A"),
            outbound_info.get("city", "Unknown City"),
            outbound_info.get("organization", "N/A"),
        )
        global outboundGeoRES
        outboundGeoRES = "{}, {}".format(
            outbound_info.get("country_code", "N/A"),
            outbound_info.get("organization", "N/A"),
        )
        logger.info("Node outbound IP : {}, Geo : {}".format(outbound_ip, outbound_geo))

        if NETFLIX_TEXT and outbound_ip != "N/A":
            logger.info("Performing netflix test LOCAL_PORT: {:d}.".format(LOCAL_PORT))
            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/64.0.3282.119 Safari/537.36 "
                }
                sum_ = 0
                global ntype
                r1 = requests.get(
                    "https://www.netflix.com/title/70242311",
                    proxies={
                        "http": "socks5h://127.0.0.1:%d" % LOCAL_PORT,
                        "https": "socks5h://127.0.0.1:%d" % LOCAL_PORT,
                    },
                    timeout=20,
                )
                if r1.status_code == 200:
                    sum_ += 1
                    soup = BeautifulSoup(r1.text, "html.parser")
                    netflix_ip_str = str(soup.find_all("script"))
                    p1 = netflix_ip_str.find("requestIpAddress")
                    netflix_ip_r = netflix_ip_str[p1 + 19 : p1 + 60]
                    p2 = netflix_ip_r.find(",")
                    netflix_ip = netflix_ip_r[0:p2]
                    logger.info("Netflix IP : " + netflix_ip)

                r2 = requests.get(
                    "https://www.netflix.com/title/70143836",
                    proxies={
                        "http": "socks5h://127.0.0.1:%d" % LOCAL_PORT,
                        "https": "socks5h://127.0.0.1:%d" % LOCAL_PORT,
                    },
                    timeout=20,
                )
                if r2.status_code == 200:
                    sum_ += 1
                # 测试连接状态

                if sum_ == 0:
                    logger.info("Netflix test result: None.")
                    ntype = "None"
                elif sum_ == 1:
                    logger.info("Netflix test result: Only Original.")
                    ntype = "Only Original"
                elif outbound_ip == netflix_ip:
                    logger.info("Netflix test result: Full Native.")
                    ntype = "Full Native"
                else:
                    logger.info("Netflix test result: Full DNS.")
                    ntype = "Full DNS"

            except Exception as e:
                logger.error("代理服务器连接异常：" + str(e.args))

        if HBO_TEXT and outbound_ip != "N/A":
            logger.info("Performing HBO max test LOCAL_PORT: {:d}.".format(LOCAL_PORT))
            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/64.0.3282.119 Safari/537.36 "
                }
                global htype
                r = requests.get(
                    "https://www.hbomax.com/",
                    proxies={
                        "http": "socks5h://127.0.0.1:%d" % LOCAL_PORT,
                        "https": "socks5h://127.0.0.1:%d" % LOCAL_PORT,
                    },
                    timeout=20,
                    allow_redirects=False,
                )

                if r.status_code == 200:
                    htype = True
                else:
                    htype = False

            except Exception as e:
                logger.error("代理服务器连接异常：" + str(e.args))

        if DISNEY_TEXT and outbound_ip != "N/A":
            logger.info(
                "Performing Disney plus test LOCAL_PORT: {:d}.".format(LOCAL_PORT)
            )
            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/64.0.3282.119 Safari/537.36 "
                }
                global dtype
                r1 = requests.get(
                    "https://www.disneyplus.com/",
                    proxies={
                        "http": "socks5h://127.0.0.1:%d" % LOCAL_PORT,
                        "https": "socks5h://127.0.0.1:%d" % LOCAL_PORT,
                    },
                    timeout=20,
                    allow_redirects=False,
                )

                r2 = requests.get(
                    "https://global.edge.bamgrid.com/token",
                    proxies={
                        "http": "socks5h://127.0.0.1:%d" % LOCAL_PORT,
                        "https": "socks5h://127.0.0.1:%d" % LOCAL_PORT,
                    },
                    headers=headers,
                    timeout=20,
                    allow_redirects=False,
                )

                if r1.status_code == 200 and r2.status_code != 403:
                    dtype = True
                else:
                    dtype = False

            except Exception as e:
                logger.error("代理服务器连接异常：" + str(e.args))

        if YOUTUBE_TEXT and outbound_ip != "N/A":
            logger.info(
                "Performing Youtube Premium test LOCAL_PORT: {:d}.".format(LOCAL_PORT)
            )
            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/64.0.3282.119 Safari/537.36 "
                }
                global ytype
                r = requests.get(
                    "https://music.youtube.com/",
                    proxies={
                        "http": "socks5h://127.0.0.1:%d" % LOCAL_PORT,
                        "https": "socks5h://127.0.0.1:%d" % LOCAL_PORT,
                    },
                    timeout=20,
                    allow_redirects=False,
                )

                if "is not available" in r.text:
                    ytype = False
                elif r.status_code == 200:
                    ytype = True
                else:
                    ytype = False

            except Exception as e:
                logger.error("代理服务器连接异常：" + str(e.args))

        if TVB_TEXT and outbound_ip != "N/A":
            logger.info("Performing TVB test LOCAL_PORT: {:d}.".format(LOCAL_PORT))
            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/64.0.3282.119 Safari/537.36 "
                }
                global ttype
                r = requests.get(
                    "https://www.mytvsuper.com/iptest.php",
                    proxies={
                        "http": "socks5h://127.0.0.1:%d" % LOCAL_PORT,
                        "https": "socks5h://127.0.0.1:%d" % LOCAL_PORT,
                    },
                    timeout=20,
                    allow_redirects=False,
                )

                if r.text.count("HK") > 0:
                    ttype = True
                else:
                    ttype = False

            except Exception as e:
                logger.error("代理服务器连接异常：" + str(e.args))

        if ABEMA_TEXT and outbound_ip != "N/A":
            logger.info("Performing Abema test LOCAL_PORT: {:d}.".format(LOCAL_PORT))
            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/64.0.3282.119 Safari/537.36 "
                }
                global atype
                r = requests.get(
                    "https://api.abema.io/v1/ip/check?device=android",
                    proxies={
                        "http": "socks5h://127.0.0.1:%d" % LOCAL_PORT,
                        "https": "socks5h://127.0.0.1:%d" % LOCAL_PORT,
                    },
                    timeout=20,
                    allow_redirects=False,
                )

                if r.text.count("Country") > 0:
                    atype = True
                else:
                    atype = False

            except Exception as e:
                logger.error("代理服务器连接异常：" + str(e.args))

        if BAHAMUT_TEXT and outbound_ip != "N/A":
            logger.info("Performing Bahamut test LOCAL_PORT: {:d}.".format(LOCAL_PORT))
            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/64.0.3282.119 Safari/537.36 "
                }
                global btype
                r = requests.get(
                    "https://ani.gamer.com.tw/ajax/token.php?adID=89422&sn=14667",
                    proxies={
                        "http": "socks5h://127.0.0.1:%d" % LOCAL_PORT,
                        "https": "socks5h://127.0.0.1:%d" % LOCAL_PORT,
                    },
                    headers=headers,
                    timeout=20,
                    allow_redirects=False,
                )

                if r.text.count("animeSn") > 0:
                    btype = True
                else:
                    btype = False

            except Exception as e:
                logger.error("代理服务器连接异常：" + str(e.args))

        return outbound_ip, outbound_geo, outbound_info.get("country_code", "N/A")

    def __tcp_ping(self, server, port):
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
                except:
                    logger.exception("")
                    pass
        return res

    @staticmethod
    def __nat_type_test():

        s = socks.socksocket(socket.AF_INET, socket.SOCK_DGRAM)
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
        except:
            logger.exception("\n")
            return None, None, None, None, None
        finally:
            s.close()

    def __start_test(self, test_mode="FULL"):
        self.__results = []
        total_nodes = len(self.__configs)
        done_nodes = 0
        node = self.__get_next_config()
        while node:
            done_nodes += 1
            try:
                cfg = node.config
                logger.info(
                    "Starting test {group} - {remarks} [{cur}/{tol}]".format(
                        group=cfg["group"],
                        remarks=cfg["remarks"],
                        cur=done_nodes,
                        tol=total_nodes,
                    )
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
                        logger.error("Port {} timeout.".format(LOCAL_PORT))
                    except ConnectionRefusedError:
                        ct += 1
                        logger.error(
                            "Connection refused on port {}.".format(LOCAL_PORT)
                        )
                    except:
                        ct += 1
                        logger.exception("An error occurred:\n")
                if not port_opened:
                    logger.error("Port {} closed.".format(LOCAL_PORT))
                    continue

                inbound_info = self.__geo_ip_inbound(cfg)
                _item["geoIP"]["inbound"]["address"] = inbound_info[0]
                _item["geoIP"]["inbound"]["info"] = inbound_info[1]
                ping_result = self.__tcp_ping(cfg["server"], cfg["server_port"])
                if isinstance(ping_result, dict):
                    for k in ping_result.keys():
                        _item[k] = ping_result[k]
                outbound_info = self.__geo_ip_outbound()
                _item["geoIP"]["outbound"]["address"] = outbound_info[0]
                _item["geoIP"]["outbound"]["info"] = outbound_info[1]

                if (
                    (not GOOGLE_PING_TEST)
                    or _item["gPing"] > 0
                    or outbound_info[2] == "CN"
                ):
                    st = SpeedTestMethods()
                    if test_mode == "WPS":
                        res = st.start_wps_test()
                        _item["webPageSimulation"]["results"] = res
                        logger.info(
                            "[{}] - [{}] - Loss: [{:.2f}%] - TCP Ping: [{:.2f}] - Google Loss: [{:.2f}%] - Google "
                            "Ping: [{:.2f}] - [WebPageSimulation]".format(
                                _item["group"],
                                _item["remarks"],
                                _item["loss"] * 100,
                                int(_item["ping"] * 1000),
                                _item["gPingLoss"] * 100,
                                int(_item["gPing"] * 1000),
                            )
                        )
                    elif test_mode == "PING":
                        nat_info = ""
                        if ssrconfig["ntt"]["enabled"]:
                            t, eip, eport, sip, sport = self.__nat_type_test()
                            _item["ntt"]["type"] = t
                            _item["ntt"]["internal_ip"] = sip
                            _item["ntt"]["internal_port"] = sport
                            _item["ntt"]["public_ip"] = eip
                            _item["ntt"]["public_port"] = eport

                            if t:
                                nat_info += " - NAT Type: " + t
                                if t != pynat.BLOCKED:
                                    nat_info += " - Internal End: {}:{}".format(
                                        sip, sport
                                    )
                                    nat_info += " - Public End: {}:{}".format(
                                        eip, eport
                                    )

                        logger.info(
                            "[{}] - [{}] - Loss: [{:.2f}%] - TCP Ping: [{:.2f}] - Google Loss: [{:.2f}%] - Google "
                            "Ping: [{:.2f}]{}".format(
                                _item["group"],
                                _item["remarks"],
                                _item["loss"] * 100,
                                int(_item["ping"] * 1000),
                                _item["gPingLoss"] * 100,
                                int(_item["gPing"] * 1000),
                                nat_info,
                            )
                        )

                    elif test_mode == "FULL":
                        nat_info = ""
                        if ssrconfig["ntt"]["enabled"]:
                            t, eip, eport, sip, sport = self.__nat_type_test()
                            _item["ntt"]["type"] = t
                            _item["ntt"]["internal_ip"] = sip
                            _item["ntt"]["internal_port"] = sport
                            _item["ntt"]["public_ip"] = eip
                            _item["ntt"]["public_port"] = eport

                            if t:
                                nat_info += " - NAT Type: " + t
                                if t != pynat.BLOCKED:
                                    nat_info += " - Internal End: {}:{}".format(
                                        sip, sport
                                    )
                                    nat_info += " - Public End: {}:{}".format(
                                        eip, eport
                                    )

                        test_res = st.start_test(self.__test_method)
                        if int(test_res[0]) == 0:
                            logger.warning("Re-testing node.")
                            test_res = st.start_test(self.__test_method)
                        global ntype
                        global htype
                        global dtype
                        global ytype
                        global ttype
                        global atype
                        global btype
                        global inboundGeoRES
                        global outboundGeoRES
                        global inboundGeoIP
                        global outboundGeoIP
                        _item["dspeed"] = test_res[0]
                        _item["maxDSpeed"] = test_res[1]
                        _item["Ntype"] = ntype
                        _item["Htype"] = htype
                        _item["Dtype"] = dtype
                        _item["Ytype"] = ytype
                        _item["Ttype"] = ttype
                        _item["Atype"] = atype
                        _item["Btype"] = btype
                        _item["InRes"] = inboundGeoRES
                        _item["OutRes"] = outboundGeoRES
                        _item["InIP"] = inboundGeoIP
                        _item["OutIP"] = outboundGeoIP
                        try:
                            _item["trafficUsed"] = test_res[3]
                            _item["rawSocketSpeed"] = test_res[2]
                        except:
                            pass

                        logger.info(
                            "[{}] - [{}] - Loss: [{:.2f}%] - TCP Ping: [{:.2f}] - Google Loss: [{:.2f}%] - Google "
                            "Ping: [{:.2f}] - AvgStSpeed: [{:.2f}MB/s] - AvgMtSpeed: [{:.2f}MB/s]{}".format(
                                _item["group"],
                                _item["remarks"],
                                _item["loss"] * 100,
                                int(_item["ping"] * 1000),
                                _item["gPingLoss"] * 100,
                                int(_item["gPing"] * 1000),
                                _item["dspeed"] / 1024 / 1024,
                                _item["maxDSpeed"] / 1024 / 1024,
                                nat_info,
                            )
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
            "Test mode : speed and tcp ping. Test method : {}".format(
                self.__test_method
            )
        )
        self.__start_test("FULL")
