import asyncio
import copy
import logging
import time

import aiohttp
from aiohttp_socks import ProxyConnector

from ssrspeed.config import ssrconfig
from ssrspeed.utils import parse_location

logger = logging.getLogger("Sub")

w_config: dict = {}
try:
    w_config = ssrconfig["webPageSimulation"]
except KeyError:
    raise Exception("Web page simulation configurations not found.")

results: list = []


async def start_web_page_simulation_test(local_host, local_port):
    while len(results):
        results.pop()
    task_list = []
    logger.info("Start web page simulation test.")
    logger.info("Proxy {}:{}".format(local_host, local_port))
    ip_loc = await parse_location(local_port)
    urls = copy.deepcopy(w_config.get("urls", []))
    if ip_loc[0]:
        if ip_loc[1] == "CN":
            urls = copy.deepcopy(w_config.get("cnUrls", []))
    logger.info("Read {} url(s).".format(len(urls)))
    for url in urls:
        task_list.append(
            asyncio.create_task(execute(url=url, host=local_host, port=local_port))
        )
    await asyncio.wait(task_list)
    return copy.deepcopy(results)


async def execute(url, host, port):
    logger.debug("{} started. Url: {}".format(asyncio.current_task().get_name(), url))
    logger.info("Testing Url : {}".format(url))
    res = {"url": url, "retCode": 0, "time": 0}
    try:
        start_time = time.time()
        async with aiohttp.ClientSession(
            connector=ProxyConnector(host=host, port=port),
            timeout=aiohttp.ClientTimeout(connect=10),
        ) as session:
            async with session.get(url) as response:
                res["retCode"] = response.status
                stop_time = time.time()
                res["time"] = stop_time - start_time
                logger.info(
                    "Url: {}, time used: {:.2f}s, code: {}.".format(
                        url, res["time"], res["retCode"]
                    )
                )
    except aiohttp.ClientTimeout:
        logger.error("Url: {} timeout.".format(url))
    except aiohttp.ClientSSLError:
        logger.error("SSL Error on : {}".format(url))
    except:
        logger.exception("Unknown Error on : {}".format(url))
    finally:
        results.append(res)


"""
def wps_thread(url, proxies):
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
