import os
import subprocess
import sys
from typing import Dict, Optional

from loguru import logger


class RequirementsCheck:
    def __init__(self, client_dir: str, databases_dir: str):
        self.__win_require: dict = {
            "Shadowsocks-libev": [
                f"{client_dir}shadowsocks-libev/obfs-local.exe",
                f"{client_dir}shadowsocks-libev/simple-obfs.exe",
                f"{client_dir}shadowsocks-libev/ss-local.exe",
                f"{client_dir}shadowsocks-libev/ss-tunnel.exe",
            ],
            "ShadowsocksR-libev": [
                f"{client_dir}shadowsocksr-libev/libssp-0.dll",
                f"{client_dir}shadowsocksr-libev/libwinpthread-1.dll",
                f"{client_dir}shadowsocksr-libev/libpcre-1.dll",
                f"{client_dir}shadowsocksr-libev/libcrypto-1_1.dll",
                f"{client_dir}shadowsocksr-libev/ssr-local.exe",
            ],
            "ShadowsocksR-C#": [f"{client_dir}shadowsocksr-win/shadowsocksr.exe"],
            "Trojan": [f"{client_dir}trojan/trojan.exe"],
            "V2Ray-Core": [
                f"{client_dir}v2ray-core/v2ctl.exe",
                f"{client_dir}v2ray-core/v2ray.exe",
            ],
            "GeoIP2 Databases": [
                f"{databases_dir}GeoLite2-City.mmdb",
                f"{databases_dir}GeoLite2-ASN.mmdb",
            ],
        }

        self.__linux_require: dict = {
            "Shadowsocks-libev": [
                f"{client_dir}shadowsocks-libev/simple-obfs",
                f"{client_dir}shadowsocks-libev/ss-local",
            ],
            "ShadowsocksR-Python": [f"{client_dir}shadowsocksr/shadowsocks/local.py"],
            "Trojan": [f"{client_dir}trojan/trojan"],
            "V2Ray-Core": [
                f"{client_dir}v2ray-core/v2ctl",
                f"{client_dir}v2ray-core/v2ray",
            ],
            "GeoIP2 Databases": [
                f"{databases_dir}GeoLite2-City.mmdb",
                f"{databases_dir}GeoLite2-ASN.mmdb",
            ],
        }

    def check(self, platform: str):
        if platform == "Windows":
            self.__checks(self.__win_require)
        elif platform in {"Linux", "MacOS"}:
            self.__linux_check(platform)
            self.__checks(self.__linux_require)
        else:
            logger.critical("Unsupported platform !")
            sys.exit(1)

    @staticmethod
    def __checks(requires: Optional[Dict[str, str]]):
        if requires is None:
            requires = {}
        for key in requires.keys():
            for require in requires[key]:
                logger.info(f"Checking {require}")
                if os.path.exists(require):
                    if os.path.isdir(require):
                        logger.warning(f"Requirement {require} not found !!!")
                else:
                    logger.warning(f"Requirement {require} not found !!!")

    def __linux_check(self, platform: str):
        if not self.__linux_check_libsodium(platform):
            logger.critical("Requirement libsodium not found !!!")
            sys.exit(1)
        self.__checks(self.__linux_require)

    #   self.__linux_check_shadowsocks()

    @staticmethod
    def __linux_check_libsodium(platform: str) -> bool:
        logger.info("Checking libsodium.")
        if platform == "MacOS":
            logger.warning(
                "MacOS does not support detection of libsodium, please ensure that libsodium is installed."
            )
            try:
                process = subprocess.Popen(
                    "brew info libsodium", shell=True, stdout=subprocess.PIPE
                )
                try:
                    out = process.communicate(timeout=15)[0]
                except subprocess.TimeoutExpired:
                    process.terminate()
                    out, errs = process.communicate()
                    logger.error(
                        out.decode("utf-8") + errs.decode("utf-8"), exc_info=True
                    )
                    return False
                logger.debug(f"brew info libsodium : {out!r}")
                if "Not installed\n" in out.decode("utf-8"):
                    logger.error("Libsodium not found.")
                    return False
                return True
            except Exception:
                logger.exception("")
                return False
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
                    logger.error(
                        out.decode("utf-8") + errs.decode("utf-8"), exc_info=True
                    )
                    return False
                logger.debug(f"ldconfig : {out!r}")
                return "libsodium" in out.decode("utf-8")
            except Exception:
                logger.exception("")
                return False

    # @staticmethod
    # def __linux_check_shadowsocks() -> bool:
    #     sslibev = False
    #     simpleobfs = False
    #     for cmdpath in os.environ["PATH"].split(":"):
    #         if not os.path.isdir(cmdpath):
    #             continue
    #         for filename in os.listdir(cmdpath):
    #             if filename == "obfs-local":
    #                 logger.info(
    #                     f'Obfs-Local found {os.path.join(cmdpath, "obfs-local")}'
    #                 )
    #                 simpleobfs = True
    #             elif filename == "ss-local":
    #                 logger.info(
    #                     f'Shadowsocks-libev found {os.path.join(cmdpath, "ss-local")}'
    #                 )
    #                 sslibev = True
    #             if simpleobfs and sslibev:
    #                 break
    #         if simpleobfs and sslibev:
    #             break
    #     if not simpleobfs:
    #         logger.warning("Simple Obfs not found !!!")
    #     if not sslibev:
    #         logger.warning("Shadowsocks-libev not found !!!")
    #     return True if (simpleobfs and sslibev) else False
