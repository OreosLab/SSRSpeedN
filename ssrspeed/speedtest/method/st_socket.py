import asyncio
import copy
import socket
import threading
import time

import socks
from loguru import logger

from ssrspeed.util import ip_loc
from ssrspeed.util.rule import DownloadRuleMatch

DEFAULT_SOCKET = socket.socket
MAX_TIME = 0
TOTAL_RECEIVED = 0
EXIT_FLAG = False
LOCK = threading.Lock()
MAX_FILE_SIZE = 100 * 1024 * 1024


def restore_socket():
    socket.socket = DEFAULT_SOCKET


def speed_test_thread(link, buffer):
    global TOTAL_RECEIVED, MAX_TIME
    logger.debug(f"Thread {threading.current_thread().ident} started.")
    link = link.replace("https://", "").replace("http://", "")
    host = link[: link.find("/")]
    request_uri = link[link.find("/") :]
    logger.debug(f"\nLink: {link}\nHost: {host}\nRequestUri: {request_uri}")

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(12)
        try:
            s.connect((host, 80))
            logger.debug(f"Connected to {host}")
        except Exception:
            logger.error(f"Connect to {host} error.")
            with LOCK:
                TOTAL_RECEIVED += 0
            return None
        s.send(
            b"GET %b HTTP/1.1\r\nHost: %b\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            b"AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36\r\n\r\n "
            % (request_uri.encode("utf-8"), host.encode("utf-8"))
        )
        logger.debug("Request sent.")
        start_time = time.time()
        received = 0
        while True:
            try:
                xx = s.recv(buffer)
            except socket.timeout:
                logger.error("Receive data timeout.")
                break
            except ConnectionResetError:
                logger.warning("Remote host closed connection.")
                break
            lxx = len(xx)
            received += lxx
            with LOCK:
                TOTAL_RECEIVED += lxx
            if received >= MAX_FILE_SIZE or EXIT_FLAG:
                break
        end_time = time.time()
        delta_time = end_time - start_time
        if delta_time >= 12:
            delta_time = 11
        s.close()
        logger.debug(
            f"Thread {threading.current_thread().ident} done,time : {delta_time}"
        )
        with LOCK:
            MAX_TIME = max(MAX_TIME, delta_time)
    except Exception:
        logger.exception("")
        return 0


async def speed_test_socket(
    file_download: dict, address: str, port: int, speed_test: bool, st_speed_test: bool
) -> tuple:
    if not speed_test:
        return 0, 0, [], 0
    workers = file_download.get("workers", 4)
    buffer_ = file_download.get("buffer", 4096)
    avg_st_speed: float = 0
    global EXIT_FLAG, MAX_TIME, TOTAL_RECEIVED, MAX_FILE_SIZE

    dlrm = DownloadRuleMatch(file_download)
    res = dlrm.get_url(await ip_loc(port))

    MAX_FILE_SIZE = res[1] * 1024 * 1024
    MAX_TIME = 0
    TOTAL_RECEIVED = 0
    EXIT_FLAG = False
    socks.set_default_proxy(socks.SOCKS5, address, port)
    socket.socket = socks.socksocket  # type: ignore

    if st_speed_test:
        for _ in range(1):
            nmsl = threading.Thread(target=speed_test_thread, args=(res[0], buffer_))
            nmsl.start()

        max_speed_list = []
        old_received = 0
        for i in range(1, 11):
            await asyncio.sleep(0.5)
            with LOCK:
                delta_received = TOTAL_RECEIVED - old_received
                old_received = TOTAL_RECEIVED
            current_speed = delta_received / 0.5
            max_speed_list.append(current_speed)
            print(
                "\r["
                + "=" * i
                + f"> [{i * 10}%/100%] [{current_speed / 1024 / 1024:.2f} MB/s]",
                end="",
            )
            if EXIT_FLAG:
                print(
                    "\r["
                    + "=" * i
                    + f"] [100%/100%] [{current_speed / 1024 / 1024:.2f} MB/s]"
                )
                break
        EXIT_FLAG = True
        for _ in range(10):
            time.sleep(0.1)
            if MAX_TIME != 0:
                break
        if MAX_TIME == 0:
            logger.error("Socket Test Error !")
            return 0, 0, [], 0

        logger.info(
            f"SingleThread: Fetched {TOTAL_RECEIVED / 1024:.2f} KB in {MAX_TIME:.2f} s."
        )

        avg_st_speed = TOTAL_RECEIVED / MAX_TIME

        MAX_TIME = 0
        TOTAL_RECEIVED = 0
        EXIT_FLAG = False

    for _ in range(workers):
        nmsl = threading.Thread(target=speed_test_thread, args=(res[0], buffer_))
        nmsl.start()

    max_speed_list = []
    current_speed = 0
    old_received = 0
    for i in range(1, 11):
        time.sleep(0.5)
        with LOCK:
            delta_received = TOTAL_RECEIVED - old_received
            old_received = TOTAL_RECEIVED
        current_speed = delta_received / 0.5
        max_speed_list.append(current_speed)
        print(
            "\r["
            + "=" * i
            + f"> [{i * 10}%/100%] [{current_speed / 1024 / 1024:.2f} MB/s]",
            end="",
        )
        if EXIT_FLAG:
            print(
                "\r["
                + "=" * i
                + f"] [100%/100%] [{current_speed / 1024 / 1024:.2f} MB/s]"
            )
            break
    EXIT_FLAG = True
    for _ in range(10):
        time.sleep(0.1)
        if MAX_TIME != 0:
            break
    if MAX_TIME == 0:
        logger.error("Socket Test Error !")
        return 0, 0, [], 0

    restore_socket()
    raw_speed_list = copy.deepcopy(max_speed_list)
    max_speed_list.sort()
    if len(max_speed_list) > 7:
        msum = sum(max_speed_list[i] for i in range(7, len(max_speed_list) - 2))
        max_speed = msum / (len(max_speed_list) - 2 - 7)
    else:
        max_speed = current_speed
    logger.info(
        f"MultiThread: Fetched {TOTAL_RECEIVED / 1024:.2f} KB in {MAX_TIME:.2f} s."
    )
    avg_speed = TOTAL_RECEIVED / MAX_TIME

    if not st_speed_test:
        avg_st_speed = avg_speed
        avg_speed = max_speed

    return avg_st_speed, avg_speed, raw_speed_list, TOTAL_RECEIVED


if __name__ == "__main__":
    from ssrspeed.path import ROOT_PATH, get_path_json

    key_path = get_path_json(ROOT_PATH)
    from ssrspeed.config import generate_config_file, load_path_config, ssrconfig

    load_path_config({"path": key_path})
    generate_config_file()
    logger.info(
        asyncio.run(
            speed_test_socket(ssrconfig["fileDownload"], "127.0.0.1", 7890, True, True)
        )
    )
