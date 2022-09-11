# coding:utf-8

import asyncio
import logging
import os
import time

from tests import root

root()

from ssrspeed.paths import KEY_PATH

LOGS_DIR = KEY_PATH["logs"]
RESULTS_DIR = KEY_PATH["results"]

if not os.path.exists(LOGS_DIR):
    os.mkdir(LOGS_DIR)
if not os.path.exists(RESULTS_DIR):
    os.mkdir(RESULTS_DIR)

loggerList = []
loggerSub = logging.getLogger("Sub")
logger = logging.getLogger(__name__)
loggerList.append(loggerSub)
loggerList.append(logger)

formatter = logging.Formatter(
    "[%(asctime)s][%(levelname)s][%(thread)d][%(filename)s:%(lineno)d]%(message)s"
)
fileHandler = logging.FileHandler(
    LOGS_DIR + time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()) + ".log",
    encoding="utf-8",
)
fileHandler.setFormatter(formatter)
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(formatter)

from ssrspeed.speedtest.methods import webpage_simulation as webPageSimulation

for item in loggerList:
    item.setLevel(logging.DEBUG)
    item.addHandler(fileHandler)
    item.addHandler(consoleHandler)


async def main():
    await webPageSimulation.start_web_page_simulation_test("127.0.0.1", 10808)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()
