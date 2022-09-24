import asyncio
import contextlib
import copy
import time
from typing import Union

import aiohttp
from aiohttp_socks import ProxyConnector
from loguru import logger

from ssrspeed.util import ip_loc
from ssrspeed.util.rule import DownloadRuleMatch


class Statistics:
    def __init__(self):
        self._stopped: bool = False
        self._total_red: Union[int, float] = 0
        self._delta_red: Union[int, float] = 0
        self._start_time: Union[int, float] = 0
        self._statistics_time: Union[int, float] = 0
        self._time_used: Union[int, float] = 0
        self._count: int = 0
        self._speed_list: list = []

    @property
    def stopped(self) -> bool:
        return self._stopped

    @property
    def time_used(self) -> Union[int, float]:
        return self._time_used

    @property
    def total_red(self) -> Union[int, float]:
        return self._total_red

    @property
    def speed_list(self) -> list:
        return copy.deepcopy(self._speed_list)

    @property
    def max_speed(self) -> Union[int, float]:
        tmp_speed_list = self.speed_list
        tmp_speed_list.sort()
        max_speed: Union[int, float] = 0
        if len(tmp_speed_list) > 12:
            msum = 0
            for i in range(12, len(tmp_speed_list) - 2):
                msum += tmp_speed_list[i]
                max_speed = msum / (len(tmp_speed_list) - 2 - 12)
        else:
            max_speed = self._total_red / self._time_used
        return max_speed

    async def record(self, received: Union[int, float]):
        cur_time = time.time()
        if not self._start_time:
            self._start_time = cur_time
        delta_time = cur_time - self._statistics_time
        self._time_used = cur_time - self._start_time
        self._total_red += received
        if delta_time > 0.5:
            self._statistics_time = cur_time
            with contextlib.suppress(StopIteration):
                self._show_progress(delta_time)
        if self.time_used > 10:
            self._stopped = True

    def show_progress_full(self):
        mb_red = self._total_red / 1024 / 1024
        print(
            "\r["
            + "=" * self._count
            + "] ["
            + (f"{mb_red / self._time_used:.2f}" if self._time_used else "0")
            + "MB/s]"
        )
        logger.info(f"Fetched {mb_red:.2f} MB in {self._time_used:.2f}s.")

    def _show_progress(self, delta_time: Union[int, float]):
        speed = (self._total_red - self._delta_red) / delta_time
        speed_mb = speed / 1024 / 1024
        self._delta_red = self._total_red
        self._count += 1
        print("\r[" + "=" * self._count + f"> [{speed_mb:.2f} MB/s]", end="")
        self._speed_list.append(speed)


async def _fetch(url: str, sta: Statistics, host: str, port: int, buffer: int):
    try:
        logger.info(f"Fetching {url} via {host}:{port}.")
        async with aiohttp.ClientSession(
            headers={"User-Agent": "curl/11.45.14"},
            connector=ProxyConnector(host=host, port=port),
            timeout=aiohttp.ClientTimeout(connect=10),
        ) as session:
            logger.debug("Session created.")
            async with session.get(url) as response:
                logger.debug("Awaiting response.")
                while not sta.stopped:
                    chunk = await response.content.read(buffer)
                    if not chunk:
                        logger.info("No chunk, task stopped.")
                        break
                    await sta.record(len(chunk))
    except Exception as e:
        logger.error(f"Download link error: {str(e)}")


async def start(file_download: dict, proxy_host: str, proxy_port: int) -> tuple:
    download_semaphore = asyncio.Semaphore(int(file_download.get("taskNum", 1)))
    workers = file_download.get("workers", 4)
    buffer_ = file_download.get("buffer", 4096)
    async with download_semaphore:
        dlrm = DownloadRuleMatch(file_download)
        res = dlrm.get_url(await ip_loc(proxy_port))
        url = res[0]
        file_size = res[1]
        logger.debug(f"Url: {url}, file_size: {file_size} MiB.")
        logger.info(f"Running st_async, workers: {workers}.")
        _sta = Statistics()
        tasks = [
            asyncio.create_task(_fetch(url, _sta, proxy_host, proxy_port, buffer_))
            for _ in range(workers)
        ]
        await asyncio.wait(tasks)
        _sta.show_progress_full()
        if _sta.time_used:
            return (
                _sta.total_red / _sta.time_used,
                _sta.max_speed,
                _sta.speed_list,
                _sta.total_red,
            )
        return 0, 0, [], 0


if __name__ == "__main__":
    from ssrspeed.config import generate_config_file, load_path_config, ssrconfig
    from ssrspeed.path import ROOT_PATH, get_path_json

    key_path = get_path_json(ROOT_PATH)
    load_path_config({"path": key_path})
    generate_config_file()
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    logger.info(asyncio.run(start(ssrconfig["fileDownload"], "127.0.0.1", 7890)))
