import socket

import socks
from loguru import logger

from ssrspeed.config import ssrconfig
from ssrspeed.speedtest.methods import (
    fast,
    google_ping,
    speedtestnet,
    st_asyncio,
    st_stream,
    stNF,
    stSocket,
    stYtb,
    tcp_ping,
    webpage_simulation,
)

LOCAL_ADDRESS = ssrconfig["localAddress"]
DEFAULT_SOCKET = socket.socket
METHOD = ssrconfig["method"]


class SpeedTestMethods:
    def __init__(self):
        self.__init_socket()

    @staticmethod
    def __init_socket():
        socket.socket = DEFAULT_SOCKET

    async def start_test(self, port, download_semaphore, method="ST_ASYNC"):
        logger.info(f"Starting speed test with {method}.")
        if method == "SPEED_TEST_NET":
            try:
                socks.set_default_proxy(socks.SOCKS5, LOCAL_ADDRESS, port)
                socket.socket = socks.socksocket
                logger.info("Initializing...")
                s = speedtestnet.Speedtest()
                logger.info("Selecting Best Server.")
                logger.info(s.get_best_server())
                logger.info("Testing Download...")
                s.download()
                result = s.results.dict()
                self.__init_socket()
                return result["download"] / 8, 0, [], 0  # bits to bytes
            except Exception:
                logger.error("", exc_info=True)
                return 0, 0, [], 0
        elif method == "FAST":
            try:
                fast.set_proxy(LOCAL_ADDRESS, port)
                result = fast.fast_com(verbose=True)
                self.__init_socket()
                # print(result)
                return result, 0, [], 0
            except Exception:
                logger.error("", exc_info=True)
                return 0, 0, [], 0
        elif method == "SOCKET":  # Old speedtest
            try:
                if METHOD == "SOCKET":
                    result = await stSocket.speed_test_socket(port)
                    return result
                if METHOD == "YOUTUBE":
                    result = stYtb.speed_test_ytb(port)
                    return result
                if METHOD == "NETFLIX":
                    result = stNF.speed_test_netflix(port)
                    return result
            except Exception:
                logger.error("", exc_info=True)
                return 0, 0, [], 0
        elif method == "YOUTUBE":
            try:
                result = await stSocket.speed_test_socket(port)
                return result
            except Exception:
                logger.error("", exc_info=True)
                return 0, 0, [], 0
        elif method == "ST_ASYNC":
            try:
                result = await st_asyncio.start(download_semaphore, LOCAL_ADDRESS, port)
                return result
            except Exception:
                logger.error("", exc_info=True)
                return 0, 0, [], 0
        else:
            raise ValueError(f"Invalid test method {method}.")

    @staticmethod
    def start_tcp_ping(server, port):
        logger.info("Testing latency to server.")
        return tcp_ping(server, port)

    @staticmethod
    def start_google_ping(port):
        logger.info("Testing latency to google.")
        return google_ping(LOCAL_ADDRESS, port)

    @staticmethod
    def start_stream_test(port, stream_cfg, outbound_ip):
        return st_stream.start_stream_test(port, stream_cfg, outbound_ip)

    @staticmethod
    def start_wps_test(port):
        return webpage_simulation.start_web_page_simulation_test(LOCAL_ADDRESS, port)
