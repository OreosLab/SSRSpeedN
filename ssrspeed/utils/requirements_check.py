import logging
import os
import subprocess
import sys
from typing import Dict, Optional

from ssrspeed.paths import KEY_PATH
from ssrspeed.utils import check_platform

logger = logging.getLogger("Sub")

CLIENTS_DIR = KEY_PATH["clients"]


class RequirementsCheck(object):
    def __init__(self):
        self.__win_require: dict = {
            "Shadowsocks-libev": [
                f"{CLIENTS_DIR}shadowsocks-libev/obfs-local.exe",
                f"{CLIENTS_DIR}shadowsocks-libev/simple-obfs.exe",
                f"{CLIENTS_DIR}shadowsocks-libev/ss-local.exe",
                f"{CLIENTS_DIR}shadowsocks-libev/ss-tunnel.exe",
            ],
            "ShadowsocksR-libev": [
                f"{CLIENTS_DIR}shadowsocksr-libev/libssp-0.dll",
                f"{CLIENTS_DIR}shadowsocksr-libev/libwinpthread-1.dll",
                f"{CLIENTS_DIR}shadowsocksr-libev/libpcre-1.dll",
                f"{CLIENTS_DIR}shadowsocksr-libev/libcrypto-1_1.dll",
                f"{CLIENTS_DIR}shadowsocksr-libev/ssr-local.exe",
            ],
            "ShadowsocksR-C#": [f"{CLIENTS_DIR}shadowsocksr-win/shadowsocksr.exe"],
            "Trojan": [f"{CLIENTS_DIR}trojan/trojan.exe"],
            "V2Ray-Core": [
                f"{CLIENTS_DIR}v2ray-core/v2ctl.exe",
                f"{CLIENTS_DIR}v2ray-core/v2ray.exe",
            ],
        }

        self.__linux_require: dict = {
            "V2Ray-Core": [
                f"{CLIENTS_DIR}v2ray-core/v2ctl",
                f"{CLIENTS_DIR}v2rayN-core/v2ray",
            ]
        }

    def check(self):
        platform = check_platform()
        if platform == "Windows":
            self.__checks(self.__win_require)
        elif platform == "Linux" or platform == "MacOS":
            self.__linux_check()
        else:
            logger.critical("Unsupported platform !")
            sys.exit(1)

    @staticmethod
    def __checks(requires: Optional[Dict[str, str]]):
        if requires is None:
            requires = {}
        for key in requires.keys():
            for require in requires[key]:
                logger.info("Checking {}".format(require))
                if os.path.exists(require):
                    if os.path.isdir(require):
                        logger.warning("Requirement {} not found !!!".format(require))
                        continue
                else:
                    logger.warning("Requirement {} not found !!!".format(require))

    def __linux_check(self):
        if not self.__linux_check_libsodium():
            logger.critical("Requirement libsodium not found !!!")
            sys.exit(1)
        self.__checks(self.__linux_require)
        self.__linux_check_shadowsocks()

    @staticmethod
    def __linux_check_libsodium() -> bool:
        logger.info("Checking libsodium.")
        if check_platform() == "MacOS":
            # logger.warning("MacOS does not support detection of libsodium,
            # please ensure that libsodium is installed.")
            try:
                process = subprocess.Popen(
                    "brew info libsodium", shell=True, stdout=subprocess.PIPE
                )
                try:
                    out = process.communicate(timeout=15)[0]
                except subprocess.TimeoutExpired:
                    process.terminate()
                    out, errs = process.communicate()
                    logger.exception(out.decode("utf-8") + errs.decode("utf-8"))
                    return False
                logger.debug("brew info libsodium : {!r}".format(out))
                if "Not installed\n" in out.decode("utf-8"):
                    logger.error("Libsodium not found.")
                    return False
                return True
            except:
                logger.exception("")
                return False
        # 	return True
        else:
            try:
                process = subprocess.Popen(
                    "ldconfig -p | grep libsodium", shell=True, stdout=subprocess.PIPE
                )
                try:
                    out = process.communicate(timeout=15)[0]
                except subprocess.TimeoutExpired:
                    process.terminate()
                    out, errs = process.communicate()
                    logger.exception(out.decode("utf-8") + errs.decode("utf-8"))
                    return False
                logger.debug("ldconfig : {!r}".format(out))
                if "libsodium" not in out.decode("utf-8"):
                    return False
                return True
            except:
                logger.exception("")
                return False

    @staticmethod
    def __linux_check_shadowsocks() -> bool:
        sslibev = False
        simpleobfs = False
        for cmdpath in os.environ["PATH"].split(":"):
            if not os.path.isdir(cmdpath):
                continue
            for filename in os.listdir(cmdpath):
                if filename == "obfs-local":
                    logger.info(
                        "Obfs-Local found {}".format(
                            os.path.join(cmdpath, "obfs-local")
                        )
                    )
                    simpleobfs = True
                elif filename == "ss-local":
                    logger.info(
                        "Shadowsocks-libev found {}".format(
                            os.path.join(cmdpath, "ss-local")
                        )
                    )
                    sslibev = True
                if simpleobfs and sslibev:
                    break
            if simpleobfs and sslibev:
                break
        if not simpleobfs:
            logger.warning("Simple Obfs not found !!!")
        if not sslibev:
            logger.warning("Shadowsocks-libev not found !!!")
        return True if (simpleobfs and sslibev) else False
