import logging
import os
import time
from typing import Union

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger("Sub")

LOCAL_PORT = 1080


def set_proxy_port(port: int):
    global LOCAL_PORT
    LOCAL_PORT = port


def speed_test_netflix(port: int) -> tuple[float, float, list[float], float]:
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--proxy-server=socks5://127.0.0.1:%d" % port)
        driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()),
            options=chrome_options,
        )
        driver.get("https://fast.com/")

        current_speed: Union[int, float] = 0
        max_speed: Union[int, float] = 0
        total_received: Union[int, float] = 0
        speed_list = []
        for i in range(0, 60):
            time.sleep(0.5)
            current_speed = float(
                driver.find_element(By.CLASS_NAME, "speed-results-container").text
            )
            unit = driver.find_element(By.CLASS_NAME, "speed-units-container").text
            speed_list.append(current_speed * 128 * 1024)
            if unit == "Kbps":
                current_speed /= 1024
            if unit == "Gbps":
                current_speed *= 1024
            if current_speed > max_speed:
                max_speed = current_speed
            total_received += current_speed * 128 * 1024
            print(
                "\r["
                + "=" * i
                + "> CurrentInternetSpeed: [%.2f MB/s]" % (current_speed / 8),
                end="",
            )
            done = len(driver.find_element(value="your-speed-message").text)
            if done:
                break

        logger.info(
            "\nNetflix test: EndSpeed {:.2f} MB/s, MaxSpeed {:.2f} MB/s.".format(
                current_speed / 8, max_speed / 8
            )
        )
        driver.close()
        os.system("taskkill /im chromedriver.exe /F")
        return (
            current_speed * 128 * 1024,
            max_speed * 128 * 1024,
            speed_list,
            total_received,
        )

    except Exception as e:
        driver.close()
        os.system("taskkill /im chromedriver.exe /F")
        logger.error("Netflix speedtest ERROR : Re-test node " + str(e.args))
        return 0, 0, [], 0
