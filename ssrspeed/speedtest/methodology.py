import logging
import socket

import socks

from ssrspeed.config import ssrconfig
from ssrspeed.speedtest.methods import (
    fast,
    google_ping,
    speedtestnet,
    st_asyncio,
    stNF,
    stSocket,
    stYtb,
    tcp_ping,
    webpage_simulation,
)

logger = logging.getLogger("Sub")

LOCAL_ADDRESS = ssrconfig["localAddress"]
LOCAL_PORT = ssrconfig["localPort"]
DEFAULT_SOCKET = socket.socket
METHOD = ssrconfig["method"]


class SpeedTestMethods(object):
    def __init__(self):
        self.__init_socket()

    # 	self.__fileUrl = "http://speedtest.dallas.linode.com/100MB-dallas.bin" #100M File
    # 	self.__proxy = {
    # 		"http":"socks5://%s:%d" % (LOCAL_ADDRESS,LOCAL_PORT),
    # 		"https":"socks5://%s:%d" % (LOCAL_ADDRESS,LOCAL_PORT)
    # 	}
    # 	self.__lock = threading.Lock()
    # 	self.__sizeList = []

    @staticmethod
    def __init_socket():
        socket.socket = DEFAULT_SOCKET

    async def start_test(self, port, method="ST_ASYNC"):
        logger.info("Starting speed test with %s." % method)
        if method == "SPEED_TEST_NET":
            try:
                socks.set_default_proxy(socks.SOCKS5, LOCAL_ADDRESS, port)
                socket.socket = socks.socksocket
                logger.info("Initializing...")
                s = speedtestnet.Speedtest()
                logger.info("Selecting Best Server...")
                logger.info(s.get_best_server())
                logger.info("Testing Download...")
                s.download()
                result = s.results.dict()
                self.__init_socket()
                return result["download"] / 8, 0, [], 0  # bits to bytes
            except:
                logger.exception("")
                return 0, 0, [], 0
        elif method == "FAST":
            try:
                fast.set_proxy(LOCAL_ADDRESS, port)
                result = fast.fast_com(verbose=True)
                self.__init_socket()
                # print(result)
                return result, 0, [], 0
            except:
                logger.exception("")
                return 0, 0, [], 0
        elif method == "SOCKET":  # Old speedtest
            try:
                if METHOD == "SOCKET":
                    result = await stSocket.speed_test_socket(port)
                    return result
                if METHOD == "YOUTUBE":
                    return stYtb.speed_test_ytb(port)
                if METHOD == "NETFLIX":
                    return stNF.speed_test_netflix(port)
            except:
                logger.exception("")
                return 0, 0, [], 0
        elif method == "YOUTUBE":
            try:
                result = await stSocket.speed_test_socket(port)
                return result
            except:
                logger.exception("")
                return 0, 0, [], 0
        elif method == "ST_ASYNC":
            try:
                return st_asyncio.start(LOCAL_ADDRESS, port)
            except:
                logger.exception("")
                return 0, 0, [], 0
        else:
            raise ValueError("Invalid test method %s." % method)

    @staticmethod
    def start_wps_test(port):
        return webpage_simulation.start_web_page_simulation_test(LOCAL_ADDRESS, port)

    @staticmethod
    def google_ping(port):
        logger.info("Testing latency to google.")
        return google_ping(LOCAL_ADDRESS, port)

    @staticmethod
    def tcp_ping(server, port):
        logger.info("Testing latency to server.")
        return tcp_ping(server, port)

        # # Old Code
        #
        # def __progress(self, current, total):
        #     print(
        #         "\r["
        #         + "=" * int(current / total * 20)
        #         + "] [%d%%/100%%]" % int(current / total * 100),
        #         end="",
        #     )
        #     if current >= total:
        #         print("\n", end="")
        #
        # def __download(self):
        #     size = 0
        #     start_time = time.time()
        #     chunk_size = 1024 * 512  # 512 KBytes
        #     rep = requests.get(self.__fileUrl, proxies=self.__proxy, stream=True)
        #     total_size = int(rep.headers["content-length"])
        #     for data in rep.iter_content(chunk_size=chunk_size):
        #         end_time = time.time()
        #         delta_time = end_time - start_time
        #         size += len(data)
        #         if delta_time < 10:
        #             continue
        #         else:
        #             break
        #     if self.__lock.acquire(timeout=5):
        #         self.__sizeList.append(size)
        #         self.__lock.release()
        #     else:
        #         raise Exception("Could not acquire lock.")
        #
        # def test_download_speed(self):
        #     size = 0
        #     print("Testing speed in 10s")
        #     thread_list = []
        #     for i in range(0, 4):
        #         t = threading.Thread(target=self.__download, args=())
        #         thread_list.append(t)
        #         t.start()
        #     while threading.active_count() > 1:
        #         print(threading.active_count())
        #         time.sleep(1)
        #     for item in self.__sizeList:
        #         size += item
        #     print(self.__sizeList)
        #     # 	print(deltaTime)
        #     print(size)
        #     speed = size / 1024 / 1024 / 10
        #     if speed < 1:
        #         return "%.2fKB" % (speed * 1000)
        #     else:
        #         return "%.2fMB" % speed
        #
        # def tcp_ping(self):
        #     pass
        #
        # def test_progress(self):
        #     for i in range(0, 51):
        #         self.__progress(i, 50)
        #         time.sleep(0.25)
