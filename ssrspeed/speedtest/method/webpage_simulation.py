import asyncio
import copy
import time

import aiohttp
from aiohttp_socks import ProxyConnector
from loguru import logger

from ssrspeed.util import parse_location

results: list = []


async def start_web_page_simulation_test(w_config, local_host, local_port):
    while results:
        results.pop()
    semaphore = asyncio.Semaphore(w_config.get("maxWorkers", 4))
    logger.info("Start web page simulation test.")
    logger.info(f"Proxy {local_host}:{local_port}")
    ip_loc = await parse_location(local_port)
    urls = copy.deepcopy(w_config.get("urls", []))
    if ip_loc[0] and ip_loc[1] == "CN":
        urls = copy.deepcopy(w_config.get("cnUrls", []))
    logger.info(f"Read {len(urls)} url(s).")
    task_list = [
        asyncio.create_task(
            execute(url=url, host=local_host, port=local_port, semaphore=semaphore)
        )
        for url in urls
    ]

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
        ) as session, semaphore, session.get(url) as response:
            res["retCode"] = response.status
            stop_time = time.time()
            res["time"] = stop_time - start_time
            logger.info(
                f"Url: {url}, time used: {res['time']:.2f}s, code: {res['retCode']}."
            )
    except asyncio.TimeoutError:
        logger.error(f"Url: {url} timeout.")
    except ConnectionResetError:
        logger.error(f"Connection reset by peer on : {url}")
    except aiohttp.TooManyRedirects:
        logger.error(f"Too many redirects on : {url}")
    except aiohttp.ClientSSLError:
        logger.error(f"SSL Error on : {url}")
    except aiohttp.ServerDisconnectedError:
        logger.error(f"Server disconnected on : {url}")
    except Exception:
        logger.exception(f"Unknown Error on : {url}")
    finally:
        results.append(res)


if __name__ == "__main__":
    W_CONFIG = {
        "enabled": True,
        "maxWorkers": 4,
        "urls": [
            "https://www.google.com.hk",
            "https://www.youtube.com",
            "https://www.bing.com",
            "https://www.github.com",
            "https://www.microsoft.com",
        ],
        "cnUrls": [
            "https://www.baidu.com",
            "https://www.weibo.com",
            "https://www.qq.com",
        ],
    }
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    print(asyncio.run(start_web_page_simulation_test(W_CONFIG, "127.0.0.1", 7890)))
