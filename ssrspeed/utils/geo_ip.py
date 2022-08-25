import logging
import re
import socket
from typing import Optional

import requests

from ssrspeed.config import ssrconfig

logger = logging.getLogger("Sub")

LOCAL_PORT = ssrconfig["localPort"]


def parse_location() -> tuple[bool, str, str, str]:
    try:
        logger.info("Starting parse location.")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/104.0.0.0 Safari/537.36",
        }
        rep = requests.get(
            "https://api.ip.sb/geoip",
            proxies={
                "http": "socks5h://127.0.0.1:%d" % LOCAL_PORT,
                "https": "socks5h://127.0.0.1:%d" % LOCAL_PORT,
            },
            headers=headers,
            timeout=5,
        )
        tmp = rep.json()
        logger.info(
            "Server Country Code : %s,Continent Code : %s,ISP : %s"
            % (tmp["country_code"], tmp["continent_code"], tmp["organization"])
        )
        return True, tmp["country_code"], tmp["continent_code"], tmp["organization"]
    except requests.exceptions.ReadTimeout:
        logger.error("Parse location timeout.")
    except:
        logger.exception("Parse location failed.")
        try:
            logger.error(rep.content)
        except:
            pass
    return False, "DEFAULT", "DEFAULT", "DEFAULT"


def check_ipv4(ip: str) -> bool:
    r = re.compile(r"\b((?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(?:(?<!\.)\b|\.)){4}")
    rm = r.match(ip)
    if rm:
        if rm.group(0) == ip:
            return True
    return False


def domain2ip(domain: str) -> str:
    logger.info("Translating {} to ipv4.".format(domain))
    """
    if check_ipv4(domain):
        return domain
    ip = "N/A"
    """
    try:
        ip = socket.gethostbyname(domain)
        return ip
    except Exception:
        logger.exception("Translate {} to ipv4 failed.".format(domain))
        return "N/A"


def ip_loc(ip: Optional[str] = "") -> dict:
    try:
        """
        if ip != "" and not check_ipv4(ip):
            logger.error("Invalid IP : {}".format(ip))
            return {}
        """
        logger.info("Starting Geo IP.")
        if ip == "N/A":
            ip = ""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/104.0.0.0 Safari/537.36",
        }
        rep = requests.get(
            "https://api.ip.sb/geoip/{}".format(ip),
            proxies={
                "http": "socks5h://127.0.0.1:%d" % LOCAL_PORT,
                "https": "socks5h://127.0.0.1:%d" % LOCAL_PORT,
            },
            headers=headers,
            timeout=5,
        )
        tmp = rep.json()
        return tmp
    except requests.exceptions.ReadTimeout:
        logger.error("Geo IP Timeout.")
        return {}
    except:
        logger.exception("Geo IP Failed.")
        try:
            logger.error(rep.content)
        except:
            pass
    return {}
