import os
import time
from typing import List, Tuple, Union

from loguru import logger
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


def speed_test_netflix(port: int) -> Tuple[float, float, List[float], float]:
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument(f"--proxy-server=socks5://127.0.0.1:{port}")
        driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()),
            options=chrome_options,
        )
        driver.get("https://fast.com/")

        current_speed: Union[int, float] = 0
        max_speed: Union[int, float] = 0
        total_received: Union[int, float] = 0
        speed_list: list = []
        for i in range(60):
            time.sleep(0.5)
            current_speed = float(
                driver.find_element(By.CLASS_NAME, "speed-results-container").text
            )
            unit = driver.find_element(By.CLASS_NAME, "speed-units-container").text
            speed_list.append(current_speed * 128 * 1024)
            if unit == "Gbps":
                current_speed *= 1024
            elif unit == "Kbps":
                current_speed /= 1024
            if current_speed > max_speed:
                max_speed = current_speed
            total_received += current_speed * 128 * 1024
            print(
                "\r["
                + "=" * i
                + f"> CurrentInternetSpeed: [{current_speed / 8:.2f} MB/s]",
                end="",
            )
            done = len(driver.find_element(value="your-speed-message").text)
            if done:
                break

        logger.info(
            "\nNetflix test: "
            f"EndSpeed {current_speed / 8:.2f} MB/s, "
            f"MaxSpeed {max_speed / 8:.2f} MB/s."
        )
        driver.close()
        return (
            current_speed * 128 * 1024,
            max_speed * 128 * 1024,
            speed_list,
            total_received,
        )

    except Exception as e:
        logger.error(f"Netflix speedtest ERROR : Re-test node {str(e.args)}")
        return 0, 0, [], 0

    finally:
        os.system("taskkill /im chromedriver.exe /F")


if __name__ == "__main__":
    logger.info(speed_test_netflix(7890))
