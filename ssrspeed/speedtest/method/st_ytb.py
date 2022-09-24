import os
import time
from typing import List, Tuple

from loguru import logger
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


def speed_test_ytb(port: int) -> Tuple[float, float, List[float], float]:
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument(f"--proxy-server=socks5://127.0.0.1:{port}")
        chrome_options.add_argument(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
        )
        driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()),
            options=chrome_options,
        )

        driver.set_window_size(3840, 2160)
        driver.get(
            "https://www.youtube.com/watch?v=mkggXE5e2yk&list=RDCMUCve7_yAZHFNipzeAGBI5t9g"
        )
        driver.find_element(By.CLASS_NAME, "ytp-large-play-button").click()
        driver.find_element(By.CLASS_NAME, "ytp-fullscreen-button").click()

        # print(driver.get_window_rect(), "\n", driver.get_window_size())
        time.sleep(0.5)
        s = driver.find_element(By.CLASS_NAME, "ytp-settings-button")
        s.click()
        logger.info(
            "Youtube view quality : "
            + driver.find_element(By.CLASS_NAME, "ytp-menu-label-secondary").text
        )
        s.click()
        t = driver.find_element(By.CLASS_NAME, "html5-main-video")
        ActionChains(driver).context_click(t).perform()
        time.sleep(0.5)
        driver.find_elements(By.CLASS_NAME, "ytp-menuitem-label")[-1].click()
        logger.info(
            "Youtube view frame : "
            + driver.find_element(By.XPATH, "//span[contains(text(),'@60')]").text
        )

        st_speed: float = 0
        max_speed: float = 0
        total_received: float = 0
        speed_list: list = []
        for i in range(20):
            time.sleep(1)
            s1 = driver.find_element(By.XPATH, "//*[contains(text(),'Kbps')]").text
            current_speed = int(s1[: s1.find(" ")])
            total_received += current_speed * 128
            speed_list.append(current_speed * 128)
            if not i:
                st_speed = current_speed
            if current_speed > max_speed:
                max_speed = current_speed
            print(
                "\r["
                + "=" * i
                + f"> [{i * 5 + 5}%/100%] [{current_speed / 8 / 1024:.2f} MB/s]",
                end="",
            )

        logger.info(
            "\nYoutube test: "
            f"StartSpeed {st_speed / 1024 / 8:.2f} MB/s, "
            f"MaxSpeed {max_speed / 8 / 1024:.2f} MB/s."
        )
        driver.close()
        return st_speed * 128, max_speed * 128, speed_list, total_received

    except Exception as e:
        logger.error(f"Youtube test ERROR : Re-testing node {str(e.args)}")
        return 0, 0, [], 0

    finally:
        os.system("taskkill /im chromedriver.exe /F")


if __name__ == "__main__":
    logger.info(speed_test_ytb(7890))
