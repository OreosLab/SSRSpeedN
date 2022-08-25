import copy
import logging
import queue
import threading
import time
from threading import Lock

import requests

from ssrspeed.config import ssrconfig
from ssrspeed.threadpool import AbstractTask, ThreadPool
from ssrspeed.utils import parse_location

logger = logging.getLogger("Sub")

w_config: dict = {}
try:
    w_config = ssrconfig["webPageSimulation"]
except KeyError:
    raise Exception("Web page simulation configurations not found.")

results: list = []
resLock: Lock = threading.Lock()
tasklist: queue.Queue = queue.Queue(maxsize=15)


def start_web_page_simulation_test(local_host: str, local_port: int) -> list:
    while len(results):
        results.pop()
    logger.info("Start web page simulation test.")
    logger.info("Proxy {}:{}".format(local_host, local_port))
    proxies = {
        "http": "socks5://{}:{}".format(local_host, local_port),
        "https": "socks5://{}:{}".format(local_host, local_port),
    }
    max_thread = w_config.get("maxThread", 4)
    ip_loc = parse_location()
    urls = copy.deepcopy(w_config.get("urls", []))
    if ip_loc[0]:
        if ip_loc[1] == "CN":
            urls = copy.deepcopy(w_config.get("cnUrls", []))
    logger.info("Read {} url(s).".format(len(urls)))
    thread_pool = ThreadPool(max_thread, tasklist)
    for url in urls:
        task = WpsTask(url=url, proxies=proxies)
        tasklist.put(task)

    thread_pool.join()
    return copy.deepcopy(results)


class WpsTask(AbstractTask):
    def __init__(self, *args, **kwargs):
        super(WpsTask, self).__init__(args, kwargs)
        self.url: str = kwargs["url"]
        self.__proxies: dict = kwargs["proxies"]

    def execute(self):
        logger.debug(
            "Thread {} started. Url: {}".format(
                threading.current_thread().ident, self.url
            )
        )
        logger.info("Testing Url : {}".format(self.url))
        res = {"url": self.url, "retCode": 0, "time": 0}
        try:
            start_time = time.time()
            rep = requests.get(self.url, proxies=self.__proxies, timeout=10)
            res["retCode"] = rep.status_code
            stop_time = time.time()
            res["time"] = stop_time - start_time
            logger.info(
                "Url: {}, time used: {:.2f}s, code: {}.".format(
                    self.url, res["time"], res["retCode"]
                )
            )
        except requests.exceptions.Timeout:
            logger.error("Url: {} timeout.".format(self.url))
        except requests.exceptions.SSLError:
            logger.error("SSL Error on : {}".format(self.url))
        except:
            logger.exception("Unknown Error on : {}".format(self.url))
        finally:
            resLock.acquire()
            results.append(res)
            resLock.release()


"""
def wps_thread(url, proxies: dict):
    logger.debug(
        "Thread {} started. Url: {}".format(threading.current_thread().ident, url)
    )
    res = {"url": url, "retCode": 0, "time": 0}
    try:
        start_time = time.time()
        rep = requests.get(url, proxies=proxies, timeout=10)
        res["retCode"] = rep.status_code
        stop_time = time.time()
        res["time"] = stop_time - start_time
        logger.info(
            "Url: {}, time used: {} ms, code: {}.".format(
                url, res["time"], res["retCode"]
            )
        )
    except requests.exceptions.Timeout:
        logger.error("Url: {} timeout.".format(url))
    except:
        logger.exception("")
    finally:
        resLock.acquire()
        results.append(res)
        resLock.release()
"""
