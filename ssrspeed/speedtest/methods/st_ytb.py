import logging
import os
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger("Sub")

# VIDEO_QUALITY = config["Youtube"]["Quality"]
LOCAL_PORT = 1080


def set_proxy_port(port: int):
    global LOCAL_PORT
    LOCAL_PORT = port


def speed_test_ytb(port: int) -> tuple[int, int, list[int], int]:
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--proxy-server=socks5://127.0.0.1:%d" % port)
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/83.0.4103.116 Safari/537.36 "
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
        # print(driver.page_source)
        # print(driver.get_window_rect())

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
        """
        driver.find_element(By.XPATH, "//div[contains(text(),'详细统计信息')]").click()
        t = driver.find_element(By.CLASS_NAME, "ytp-scrubber-container")
        ac = ActionChains(driver)
        ac.click_and_hold(t)
        ac.move_by_offset(300, 0)
        ac.release()
        ac.perform()
        """
        logger.info(
            "Youtube view frame : "
            + driver.find_element(By.XPATH, "//span[contains(text(),'@60')]").text
        )

        st_speed = 0
        max_speed = 0
        total_received = 0
        speed_list = []
        for i in range(0, 20):
            time.sleep(1)
            s1 = driver.find_element(By.XPATH, "//*[contains(text(),'Kbps')]").text
            current_speed = int(s1[0 : s1.find(" ")])
            total_received += current_speed * 128
            speed_list.append(current_speed * 128)
            if not i:
                st_speed = current_speed
            if current_speed > max_speed:
                max_speed = current_speed
            print(
                "\r["
                + "=" * i
                + "> [%d%%/100%%] [%.2f MB/s]"
                % (int(i * 5 + 5), current_speed / 8 / 1024),
                end="",
            )

        driver.close()
        os.system("taskkill /im chromedriver.exe /F")
        logger.info(
            "\nYoutube test: StartSpeed {:.2f} MB/s, MaxSpeed {:.2f} MB/s.".format(
                st_speed / 1024 / 8, max_speed / 8 / 1024
            )
        )
        return st_speed * 128, max_speed * 128, speed_list, total_received

    except Exception as e:
        driver.close()
        os.system("taskkill /im chromedriver.exe /F")
        logger.error("Youtube test ERROR : Re-testing node " + str(e.args))
        return 0, 0, [], 0
