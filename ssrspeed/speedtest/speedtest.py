import asyncio
import contextlib
import copy
import os
import socket

import geoip2.database
import socks
from geoip2.errors import AddressNotFoundError
from loguru import logger

from ssrspeed.config import ssrconfig
from ssrspeed.launcher import (
    ShadowsocksClient,
    ShadowsocksRClient,
    TrojanClient,
    V2RayClient,
)
from ssrspeed.speedtest.methodology import SpeedTestMethods
from ssrspeed.util import async_check_port, domain2ip, get_ip_info, ip_loc

CLIENTS_DIR = ssrconfig["path"]["clients"]
DATABASES_DIR = ssrconfig["path"]["databases"]
TMP_DIR = ssrconfig["path"]["tmp"]
LOCAL_ADDRESS = ssrconfig.get("localAddress", "127.0.0.1")
LOCAL_PORT = int(ssrconfig.get("localPort", 10870))
MAX_CONNECTIONS = int(ssrconfig.get("maxConnections", 50))
FAST_SPEED = ssrconfig.get("fastSpeed", False)
GEOIP_TEST = ssrconfig.get("geoip", True)
STREAM_TEST = ssrconfig.get("stream", True)
PING_TEST = ssrconfig.get("ping", True)
GOOGLE_PING_TEST = ssrconfig.get("gping", True)
WPS_CONFIG = ssrconfig.get("webPageSimulation", {})
WPS_TEST = WPS_CONFIG.get("enabled", False)
FILE_DOWNLOAD = ssrconfig.get("fileDownload", {})
SPEED_TEST = ssrconfig.get("speed", False)
SOCKET_METHOD = ssrconfig.get("method", "SOCKET")
ST_SPEED_TEST = ssrconfig.get("StSpeed", False)
NTT_TEST = ssrconfig.get("ntt", {}).get("enabled", True)


class SpeedTest:
    def __init__(self, args, parser, method="ST_ASYNC"):
        self.__configs = parser.nodes
        self.__debug = args.debug
        self.__connection = args.max_connections or MAX_CONNECTIONS
        self.__test_method = method
        self.__results = []
        self.__current = {}
        self.__city_data = None
        self.__ans_data = None
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
        self.__stream_cfg = {
            "NETFLIX_TEST": ssrconfig["netflix"],
            "HBO_TEST": ssrconfig["hbo"],
            "DISNEY_TEST": ssrconfig["disney"],
            "YOUTUBE_TEST": ssrconfig["youtube"],
            "ABEMA_TEST": ssrconfig["abema"],
            "BAHAMUT_TEST": ssrconfig["bahamut"],
            "DAZN_TEST": ssrconfig["dazn"],
            "TVB_TEST": ssrconfig["tvb"],
            "BILIBILI_TEST": ssrconfig["bilibili"],
        }

    def __get_base_result(self):
        return copy.deepcopy(self.__base_result)

    @staticmethod
    def __get_client(client_type, file):
        client = None
        if client_type == "Shadowsocks":
            client = ShadowsocksClient(CLIENTS_DIR, file)
        elif client_type == "ShadowsocksR":
            client = ShadowsocksRClient(CLIENTS_DIR, file)
        elif client_type == "Trojan":
            client = TrojanClient(CLIENTS_DIR, file)
        elif client_type == "V2Ray":
            client = V2RayClient(CLIENTS_DIR, file)
        return client

    def reset_status(self):
        self.__results = []
        self.__current = {}

    def get_result(self):
        return self.__results

    def get_current(self):
        return self.__current

    def load_geo_info(self):
        self.__city_data = geoip2.database.Reader(f"{DATABASES_DIR}GeoLite2-City.mmdb")
        self.__ans_data = geoip2.database.Reader(f"{DATABASES_DIR}GeoLite2-ASN.mmdb")

    def query_geo_local(self, ip):
        country, city, organization = "N/A", "Unknown City", "N/A"
        try:
            country_info = self.__city_data.city(ip).country
            country = country_info.names.get("en", "N/A")
            city = self.__city_data.city(ip).city.names.get("en", "Unknown City")
            organization = self.__ans_data.asn(ip).autonomous_system_organization
        except ValueError as e:
            logger.error(e)
        except AddressNotFoundError as e:
            logger.error(e)
        return {"country": country, "city": city, "organization": organization}

    def __geo_ip_inbound(self, config):
        inbound_ip = domain2ip(config["server"])
        inbound_geo = self.query_geo_local(inbound_ip)
        inbound_geo_res = f"{inbound_geo.get('city', 'Unknown City')}, {inbound_geo.get('organization', 'N/A')}"
        inbound_info = (
            f"{inbound_geo.get('country', 'N/A')} {inbound_geo.get('city', 'Unknown City')}, "
            f"{inbound_geo.get('organization', 'N/A')}"
        )
        return inbound_ip, inbound_geo_res, inbound_info

    @staticmethod
    async def __geo_ip_outbound(port, semaphore):
        async with semaphore:
            outbound_geo = await ip_loc(port)
        outbound_ip = outbound_geo.get("ip", "N/A")
        outbound_geo_res = f"{outbound_geo.get('city', 'Unknown City')}, {outbound_geo.get('organization', 'N/A')}"
        outbound_info = (
            f"{outbound_geo.get('country', 'N/A')} {outbound_geo.get('city', 'Unknown City')}, "
            f"{outbound_geo.get('organization', 'N/A')}"
        )
        return outbound_ip, outbound_geo_res, outbound_info

    async def __ping(self, server, server_port, address, port):
        latency_test = None
        st = SpeedTestMethods()

        res = {
            "loss": self.__base_result["loss"],
            "ping": self.__base_result["ping"],
            "rawTcpPingStatus": self.__base_result["rawTcpPingStatus"],
            "gPing": self.__base_result["gPing"],
            "gPingLoss": self.__base_result["gPingLoss"],
            "rawGooglePingStatus": self.__base_result["rawGooglePingStatus"],
        }

        if PING_TEST:
            latency_test = await st.start_tcp_ping(server, server_port)
            res["loss"] = 1 - latency_test[1]
            res["ping"] = latency_test[0]
            res["rawTcpPingStatus"] = latency_test[2]
            logger.debug(latency_test)

        if ((not PING_TEST) or (latency_test[0] > 0)) and GOOGLE_PING_TEST:
            try:
                google_ping_test = await st.start_google_ping(address, port)
                res["gPing"] = google_ping_test[0]
                res["gPingLoss"] = 1 - google_ping_test[1]
                res["rawGooglePingStatus"] = google_ping_test[2]
            except Exception:
                logger.exception("")

        return res

    @staticmethod
    def __nat_type_test(port):
        s = socks.socksocket(type=socket.SOCK_DGRAM)
        s.set_proxy(socks.PROXY_TYPE_SOCKS5, LOCAL_ADDRESS, port)
        sport = ssrconfig["ntt"]["internal_port"]
        try:
            logger.info("Performing UDP NAT Type Test.")
            t, eip, eport, sip = get_ip_info(
                source_ip=ssrconfig["ntt"]["internal_ip"],
                source_port=sport,
                include_internal=True,
                sock=s,
            )
            return t, eip, eport, sip, sport
        except (socket.gaierror, TypeError, ConnectionError) as e:
            logger.error(f"NAT Type Test: {repr(e)}")
            return None, None, None, None, None
        except Exception:
            logger.exception("NAT Type Test: ")
            return None, None, None, None, None
        finally:
            s.close()

    async def __fast_start_test(
        self, _item, cfg, address, port, geo_ip_semaphore, **kwargs
    ):
        node_info = f"[{_item['group']}] - [{_item['remarks']}] "
        geoip_log = ""
        tcp_ping_log = ""
        google_ping_log = ""
        wps_log = ""
        speed_log = ""
        nat_info = ""
        outbound_ip = "N/A"
        stream_task = None
        ping_task = None
        wps_task = None
        speed_task = None
        st = SpeedTestMethods()
        task_list = []

        if (
            kwargs.get("default", False)
            and GEOIP_TEST
            or kwargs.get("geoip_test", False)
        ):
            inbound_ip, inbound_geo_res, inbound_info = self.__geo_ip_inbound(cfg)
            (
                outbound_ip,
                outbound_geo_res,
                outbound_info,
            ) = await self.__geo_ip_outbound(port, geo_ip_semaphore)

            geoip_log = (
                f"* Inbound IP : {inbound_ip}, Geo : {inbound_info} "
                f"* Outbound IP : {outbound_ip}, Geo : {outbound_info} "
            )

            _item["geoIP"]["inbound"]["address"] = inbound_ip
            _item["InIP"] = inbound_ip
            _item["InRes"] = inbound_geo_res
            _item["geoIP"]["inbound"]["info"] = inbound_info
            _item["geoIP"]["outbound"]["address"] = outbound_ip
            _item["OutIP"] = outbound_ip
            _item["OutRes"] = outbound_geo_res
            _item["geoIP"]["outbound"]["info"] = outbound_info

        if (
            kwargs.get("default", False)
            and STREAM_TEST
            or kwargs.get("stream_test", False)
        ):
            stream_task = asyncio.create_task(
                st.start_stream_test(port, self.__stream_cfg, outbound_ip)
            )
            task_list.append(stream_task)

        if kwargs.get("default", False) and PING_TEST or kwargs.get("ping_test", False):
            ping_task = asyncio.create_task(
                self.__ping(cfg["server"], cfg["server_port"], address, port)
            )
            task_list.append(ping_task)

        if kwargs.get("default", False) and WPS_TEST or kwargs.get("wps_test", False):
            wps_task = asyncio.create_task(st.start_wps_test(WPS_CONFIG, address, port))
            task_list.append(wps_task)

        if (
            kwargs.get("default", False)
            and SPEED_TEST
            or kwargs.get("speed_test", False)
        ):
            speed_task = asyncio.create_task(
                st.start_test(
                    address=address,
                    port=port,
                    file_download=FILE_DOWNLOAD,
                    speed_test=SPEED_TEST,
                    method=self.__test_method,
                    socket_method=SOCKET_METHOD,
                    st_speed_test=ST_SPEED_TEST,
                )
            )
            task_list.append(speed_task)

        if kwargs.get("default", False) and NTT_TEST or kwargs.get("ntt_test", False):
            t, eip, eport, sip, sport = self.__nat_type_test(port)
            _item["ntt"]["type"] = t
            _item["ntt"]["internal_ip"] = sip
            _item["ntt"]["internal_port"] = sport
            _item["ntt"]["public_ip"] = eip
            _item["ntt"]["public_port"] = eport
            if t:
                nat_info = f"* NAT Type: {t} "
                if t != "Blocked":
                    nat_info += f"* Internal End: {sip}:{sport} "
                    nat_info += f"* Public End: {eip}:{eport} "

        await asyncio.wait(task_list)

        if stream_task:
            result = stream_task.result()
            _item.update(result)

        if ping_task:
            ping_res = ping_task.result()
            tcp_ping_log = (
                f"* Loss: [{ping_res['loss'] * 100:.2f}%] "
                f"* TCP Ping: [{ping_res['ping'] * 1000:.2f}] "
            )
            google_ping_log = (
                f"* Loss: [{ping_res['gPingLoss'] * 100:.2f}%] "
                f"* Google Ping: [{ping_res['gPing'] * 1000:.2f}] "
            )
            _item["ping"] = ping_res["ping"]
            _item["loss"] = ping_res["loss"]
            _item["rawTcpPingStatus"] = ping_res["rawTcpPingStatus"]
            _item["gPing"] = ping_res["gPing"]
            _item["gPingLoss"] = ping_res["gPingLoss"]
            _item["rawGooglePingStatus"] = ping_res["rawGooglePingStatus"]

        if wps_task:
            res = wps_task.result()
            wps_log = "[WebPageSimulation] "
            _item["webPageSimulation"]["results"] = res

        if speed_task:
            test_res = speed_task.result()
            if int(test_res[0]) == 0:
                logger.warning("Re-testing node.")
                test_res = await st.start_test(
                    address=address,
                    port=port,
                    file_download=FILE_DOWNLOAD,
                    speed_test=SPEED_TEST,
                    method=self.__test_method,
                    socket_method=SOCKET_METHOD,
                    st_speed_test=ST_SPEED_TEST,
                )

            speed_log = (
                f"* AvgStSpeed: [{test_res[0] / 1024 / 1024:.2f}MB/s] "
                f"* AvgMtSpeed: [{test_res[1] / 1024 / 1024:.2f}MB/s] "
            )

            _item["dspeed"] = test_res[0]
            _item["maxDSpeed"] = test_res[1]
            with contextlib.suppress(Exception):
                _item["trafficUsed"] = test_res[3]
                _item["rawSocketSpeed"] = test_res[2]
        logger.info(
            node_info
            + geoip_log
            + tcp_ping_log
            + google_ping_log
            + wps_log
            + speed_log
            + nat_info
        )

    async def __base_start_test(
        self, _item, cfg, address, port, geo_ip_semaphore, **kwargs
    ):
        node_info = f"[{_item['group']}] - [{_item['remarks']}] "
        geoip_log = ""
        tcp_ping_log = ""
        google_ping_log = ""
        wps_log = ""
        speed_log = ""
        nat_info = ""
        outbound_ip = "N/A"
        st = SpeedTestMethods()

        if (
            kwargs.get("default", False)
            and GEOIP_TEST
            or kwargs.get("geoip_test", False)
        ):
            inbound_ip, inbound_geo_res, inbound_info = self.__geo_ip_inbound(cfg)
            (
                outbound_ip,
                outbound_geo_res,
                outbound_info,
            ) = await self.__geo_ip_outbound(port, geo_ip_semaphore)

            geoip_log = (
                f"- Inbound IP : {inbound_ip}, Geo : {inbound_info} "
                f"- Outbound IP : {outbound_ip}, Geo : {outbound_info} "
            )

            _item["geoIP"]["inbound"]["address"] = inbound_ip
            _item["InIP"] = inbound_ip
            _item["InRes"] = inbound_geo_res
            _item["geoIP"]["inbound"]["info"] = inbound_info
            _item["geoIP"]["outbound"]["address"] = outbound_ip
            _item["OutIP"] = outbound_ip
            _item["OutRes"] = outbound_geo_res
            _item["geoIP"]["outbound"]["info"] = outbound_info

        if (
            kwargs.get("default", False)
            and STREAM_TEST
            or kwargs.get("stream_test", False)
        ):
            result = await st.start_stream_test(port, self.__stream_cfg, outbound_ip)
            _item.update(result)

        if (
            kwargs.get("default", False)
            and (PING_TEST or GOOGLE_PING_TEST)
            or kwargs.get("ping_test", False)
        ):
            ping_res = await self.__ping(
                cfg["server"], cfg["server_port"], address, port
            )

            tcp_ping_log = (
                f"- Loss: [{ping_res['loss'] * 100:.2f}%] "
                f"- TCP Ping: [{ping_res['ping'] * 1000:.2f}] "
            )
            google_ping_log = (
                f"- Loss: [{ping_res['gPingLoss'] * 100:.2f}%] "
                f"- Google Ping: [{ping_res['gPing'] * 1000:.2f}] "
            )

            _item["ping"] = ping_res["ping"]
            _item["loss"] = ping_res["loss"]
            _item["rawTcpPingStatus"] = ping_res["rawTcpPingStatus"]
            _item["gPing"] = ping_res["gPing"]
            _item["gPingLoss"] = ping_res["gPingLoss"]
            _item["rawGooglePingStatus"] = ping_res["rawGooglePingStatus"]

        if kwargs.get("default", False) and WPS_TEST or kwargs.get("wps_test", False):
            res = await st.start_wps_test(WPS_CONFIG, address, port)
            wps_log = "[WebPageSimulation] "
            _item["webPageSimulation"]["results"] = res

        if (
            kwargs.get("default", False)
            and SPEED_TEST
            or kwargs.get("speed_test", False)
        ):
            test_res = await st.start_test(
                address=address,
                port=port,
                file_download=FILE_DOWNLOAD,
                speed_test=SPEED_TEST,
                method=self.__test_method,
                socket_method=SOCKET_METHOD,
                st_speed_test=ST_SPEED_TEST,
            )
            if int(test_res[0]) == 0:
                logger.warning("Re-testing node.")
                test_res = await st.start_test(
                    address=address,
                    port=port,
                    file_download=FILE_DOWNLOAD,
                    speed_test=SPEED_TEST,
                    method=self.__test_method,
                    socket_method=SOCKET_METHOD,
                    st_speed_test=ST_SPEED_TEST,
                )

            speed_log = (
                f"- AvgStSpeed: [{test_res[0] / 1024 / 1024:.2f}MB/s] "
                f"- AvgMtSpeed: [{test_res[1] / 1024 / 1024:.2f}MB/s] "
            )

            _item["dspeed"] = test_res[0]
            _item["maxDSpeed"] = test_res[1]
            with contextlib.suppress(Exception):
                _item["trafficUsed"] = test_res[3]
                _item["rawSocketSpeed"] = test_res[2]
        if kwargs.get("default", False) and NTT_TEST or kwargs.get("ntt_test", False):
            t, eip, eport, sip, sport = self.__nat_type_test(port)
            _item["ntt"]["type"] = t
            _item["ntt"]["internal_ip"] = sip
            _item["ntt"]["internal_port"] = sport
            _item["ntt"]["public_ip"] = eip
            _item["ntt"]["public_port"] = eport
            if t:
                nat_info = f"- NAT Type: {t} "
                if t != "Blocked":
                    nat_info += f"- Internal End: {sip}:{sport} "
                    nat_info += f"- Public End: {eip}:{eport} "

        logger.info(
            node_info
            + geoip_log
            + tcp_ping_log
            + google_ping_log
            + wps_log
            + speed_log
            + nat_info
        )

    async def __async__start_test(
        self, node, dic, lock, port_queue, inner_method, geo_ip_semaphore, **kwargs
    ):
        port = await port_queue.get()
        cfg = node.config
        cfg.update({"local_port": port})
        async with lock:
            dic["done_nodes"] += 1
            logger.info(
                f"Starting test {cfg['group']} - {cfg['remarks']} [{dic['done_nodes']}/{dic['total_nodes']}]"
            )
        name = asyncio.current_task().get_name()
        file_ = f"{TMP_DIR}{name}.json"
        client = self.__get_client(node.node_type, file_)
        if not client:
            logger.warning(f"Unknown Node Type: {node.node_type}.")
            return False
        _item = self.__get_base_result()
        _item["group"] = cfg["group"]
        _item["remarks"] = cfg["remarks"]
        self.__current = _item
        cfg["server_port"] = int(cfg["server_port"])
        _item["port"] = cfg["server_port"]
        await client.start_client(cfg, self.__debug)

        # Check clients started
        if not client.check_alive():
            for _ in range(3):
                await client.start_client(cfg, self.__debug)
                if client.check_alive():
                    break
            else:
                logger.error("Failed to start clients.")
                return False
        logger.info("Client started.")

        # Check port
        if not await async_check_port(port):
            for _ in range(3):
                if await async_check_port(port):
                    break
            else:
                logger.error(f"Port {port} closed.")
                return False

        await inner_method(_item, cfg, LOCAL_ADDRESS, port, geo_ip_semaphore, **kwargs)

        self.__results.append(_item)
        port_queue.put_nowait(port)
        if client:
            client.stop_client()
        if os.path.exists(file_):
            os.remove(file_)

    async def __run(self, **kwargs):
        lock = asyncio.Lock()
        geo_ip_semaphore = asyncio.Semaphore()
        port_queue = asyncio.Queue()
        dic = {"done_nodes": 0, "total_nodes": len(self.__configs)}
        # 根据配置文件是否选择极速模式
        fast_method = self.__fast_start_test if FAST_SPEED else self.__base_start_test

        # 初始化端口范围
        for i in range(LOCAL_PORT, LOCAL_PORT + self.__connection):
            port_queue.put_nowait(i)

        # 布置异步任务
        task_list = [
            asyncio.create_task(
                self.__async__start_test(
                    node, dic, lock, port_queue, fast_method, geo_ip_semaphore, **kwargs
                )
            )
            for node in self.__configs
        ]

        await asyncio.wait(task_list)

    def __start_test(self, **kwargs):
        self.__results = []
        self.load_geo_info()
        if os.name == "nt":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.__run(**kwargs))
        loop.close()
        self.__current = {}

    def default_test(self):
        logger.info("Test Default")
        self.__start_test(default=True)

    def web_page_simulation(self):
        logger.info("Test mode : Web Page Simulation")
        self.__start_test(geoip_test=True, ping_test=True, wps_test=True)

    def ping_only(self):
        logger.info("Test mode : ping only")
        self.__start_test(ping_test=True)

    def stream_only(self):
        logger.info("Test mode : stream only")
        self.__start_test(stream_test=True)

    def full_test(self):
        logger.info(f"Test mode : All. Test method : {self.__test_method}")
        self.__start_test(
            geoip_test=True,
            stream_test=True,
            ping_test=True,
            ntt_test=True,
            speed_test=True,
        )
