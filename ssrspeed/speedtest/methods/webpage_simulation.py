import asyncio
import copy
import time

import aiohttp
from aiohttp_socks import ProxyConnector
from loguru import logger

from ssrspeed.config import ssrconfig
from ssrspeed.utils import parse_location

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
    semaphore = asyncio.Semaphore(w_config.get("maxWorkers", 4))
    logger.info("Start web page simulation test.")
    logger.info(f"Proxy {local_host}:{local_port}")
    ip_loc = await parse_location(local_port)
    urls = copy.deepcopy(w_config.get("urls", []))
    if ip_loc[0]:
        if ip_loc[1] == "CN":
            urls = copy.deepcopy(w_config.get("cnUrls", []))
    logger.info(f"Read {len(urls)} url(s).")
    for url in urls:
        task_list.append(
            asyncio.create_task(
                execute(url=url, host=local_host, port=local_port, semaphore=semaphore)
            )
        )
    await asyncio.wait(task_list)
    return copy.deepcopy(results)


async def execute(url, host, port, semaphore):
    logger.debug(f"{asyncio.current_task().get_name()} started. Url: {url}")
    logger.info(f"Testing Url : {url}")
    res = {"url": url, "retCode": 0, "time": 0}
    try:
        start_time = time.time()
        async with aiohttp.ClientSession(
            connector=ProxyConnector(host=host, port=port),
            timeout=aiohttp.ClientTimeout(connect=10),
        ) as session:
            async with semaphore:
                async with session.get(url) as response:
                    res["retCode"] = response.status
                    stop_time = time.time()
                    res["time"] = stop_time - start_time
                    logger.info(
                        f"Url: {url}, time used: {res['time']:.2f}s, code: {res['retCode']}."
                    )
    except asyncio.TimeoutError:
        logger.error(f"Url: {url} timeout.")
    except aiohttp.ClientSSLError:
        logger.error(f"SSL Error on : {url}")
    except Exception:
        logger.error(f"Unknown Error on : {url}", exc_info=True)
    finally:
        results.append(res)


if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    print(asyncio.run(start_web_page_simulation_test("127.0.0.1", 7890)))
