import socket

import socks
from loguru import logger

from ssrspeed.speedtest.method import (
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


class SpeedTestMethods:

    DEFAULT_SOCKET = socket.socket

    def __init__(self):
        self.__init_socket()

    @classmethod
    def __init_socket(cls):
        socket.socket = cls.DEFAULT_SOCKET

    async def start_test(self, **kwargs):
        address = kwargs.get("address", "127.0.0.1")
        port = kwargs.get("port", 10870)
        file_download = kwargs.get("file_download", {})
        speed_test = kwargs.get("speed_test", False)
        method = kwargs.get("method", "ST_ASYNC")
        socket_method = kwargs.get("socket_method", "SOCKET")
        st_speed_test = kwargs.get("st_speed_test", False)

        logger.info(f"Starting speed test with {method}.")
        if method == "ST_ASYNC":
            try:
                result = await st_asyncio.start(file_download, address, port)
                return result
            except Exception:
                logger.exception("")
        elif method == "SOCKET":  # Old speedtest
            try:
                if socket_method == "SOCKET":
                    result = await stSocket.speed_test_socket(
                        file_download, address, port, speed_test, st_speed_test
                    )
                    return result
                if socket_method == "YOUTUBE":
                    result = stYtb.speed_test_ytb(port)
                    return result
                if socket_method == "NETFLIX":
                    result = stNF.speed_test_netflix(port)
                    return result
            except Exception:
                logger.exception("")
        elif method == "SPEED_TEST_NET":
            try:
                socks.set_default_proxy(socks.SOCKS5, address, port)
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
                logger.exception("")
        elif method == "FAST":
            try:
                fast.set_proxy(address, port)
                result = fast.fast_com(verbose=True)
                self.__init_socket()
                #   print(result)
                return result, 0, [], 0
            except Exception:
                logger.exception("")
        elif method == "YOUTUBE":
            try:
                result = await stSocket.speed_test_socket(
                    file_download, address, port, speed_test, st_speed_test
                )
                return result
            except Exception:
                logger.exception("")
        else:
            raise ValueError(f"Invalid test method {method}.")
        return 0, 0, [], 0

    @staticmethod
    def start_tcp_ping(server, port):
        logger.info("Testing latency to server.")
        return tcp_ping(server, port)

    @staticmethod
    def start_google_ping(address, port):
        logger.info("Testing latency to google.")
        return google_ping(address, port)

    @staticmethod
    def start_stream_test(port, stream_cfg, outbound_ip):
        return st_stream.start_stream_test(port, stream_cfg, outbound_ip)

    @staticmethod
    def start_wps_test(wps_config, address, port):
        return webpage_simulation.start_web_page_simulation_test(
            wps_config, address, port
        )
