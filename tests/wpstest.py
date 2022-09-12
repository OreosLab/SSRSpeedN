# coding:utf-8
import asyncio
import os
import sys
import time

from tests import root

root()

from loguru import logger

from ssrspeed.paths import KEY_PATH

LOGS_DIR = KEY_PATH["logs"]
RESULTS_DIR = KEY_PATH["results"]

if not os.path.exists(LOGS_DIR):
    os.mkdir(LOGS_DIR)
if not os.path.exists(RESULTS_DIR):
    os.mkdir(RESULTS_DIR)

LOG_FILE = f"{LOGS_DIR}{time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())}.log"
handlers = [
    {
        "sink": sys.stdout,
        "level": "INFO",
        "format": "[<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green>][<level>{level}</level>]"
        "[<yellow>{file}</yellow>:<cyan>{line}</cyan>]: <level>{message}</level>",
        "colorize": True,  # 自定义配色
        "serialize": False,  # 以 JSON 数据格式打印
        "backtrace": True,  # 是否显示完整的异常堆栈跟踪
        "diagnose": True,  # 异常跟踪是否显示触发异常的方法或语句所使用的变量，生产环境应设为 False
        "enqueue": True,  # 默认线程安全。若想实现协程安全 或 进程安全，该参数设为 True
        "catch": True,  # 捕获异常
    },
    {
        "sink": LOG_FILE,
        "level": "INFO",
        "format": "[{time:YYYY-MM-DD HH:mm:ss.SSS}][{level}][{file}:{line}]: {message}",
        "serialize": False,
        "backtrace": True,
        "diagnose": True,
        "enqueue": True,
        "catch": True,
    },
]

from ssrspeed.speedtest.methods import webpage_simulation as webPageSimulation

logger.configure(handlers=handlers)
logger.enable("__main__")


async def main():
    await webPageSimulation.start_web_page_simulation_test("127.0.0.1", 10808)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()
