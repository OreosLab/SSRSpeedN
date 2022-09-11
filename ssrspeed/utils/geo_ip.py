import asyncio.exceptions
import re
import socket

import aiohttp
import python_socks
from aiohttp_socks import ProxyConnector
from loguru import logger


async def parse_location(port):
    try:
        logger.info("Starting parse location.")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/104.0.0.0 Safari/537.36",
        }
        url = "https://api.ip.sb/geoip"
        async with aiohttp.ClientSession(
            headers=headers,
            connector=ProxyConnector(host="127.0.0.1", port=port),
            timeout=aiohttp.ClientTimeout(connect=10, sock_connect=10, sock_read=10),
        ) as session:
            async with session.get(url=url) as response:
                tmp = await response.json()
                logger.info(
                    f'Server Country Code : {tmp["country_code"]}, '
                    f'Continent Code : {tmp["continent_code"]}, '
                    f'ISP : {tmp["organization"]}'
                )
            return True, tmp["country_code"], tmp["continent_code"], tmp["organization"]
    except asyncio.TimeoutError:
        logger.error("Parse location timeout.")
    except Exception:
        logger.error("Parse location failed.", exc_info=True)
        try:
            logger.error(response.content)
        except Exception:
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
    logger.info(f"Translating {domain} to ipv4.")
    """
    if check_ipv4(domain):
        return domain
    ip = "N/A"
    """
    try:
        ip = socket.gethostbyname(domain)
        return ip
    except Exception:
        logger.error(f"Translate {domain} to ipv4 failed.", exc_info=True)
        return "N/A"


async def ip_loc(port):
    try:
        """
        if ip != "" and not check_ipv4(ip):
            logger.error(f"Invalid IP : {ip}")
            return {}
        """
        logger.info("Starting Geo IP.")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/104.0.0.0 Safari/537.36",
        }
        url = f"https://api.ip.sb/geoip"
        async with aiohttp.ClientSession(
            headers=headers,
            connector=ProxyConnector(host="127.0.0.1", port=port),
            timeout=aiohttp.ClientTimeout(connect=10, sock_connect=10, sock_read=10),
        ) as session:
            async with session.get(url=url) as response:
                tmp = await response.json()
                return tmp
    except aiohttp.ClientOSError:
        logger.error("Geo IP ClientOSError")
        return {}
    except python_socks._errors.ProxyTimeoutError:
        logger.error("Geo IP Proxy Timeout.")
        return {}
    except python_socks._errors.ProxyConnectionError:
        logger.error("Geo IP Proxy Connection Error.")
        return {}
    except asyncio.TimeoutError:
        logger.error("Geo IP Timeout.")
        return {}
    except ConnectionResetError:
        logger.error("Geo IP Reset.")
        return {}
    except aiohttp.ContentTypeError:
        logger.error("Geo IP Connection closed.")
        return {}
    except asyncio.IncompleteReadError:
        logger.error("Geo IP Incomplete Read.")
        return {}
    except Exception:
        logger.error("Geo IP Failed.", exc_info=True)
        try:
            logger.error(response.content)
        except Exception:
            return {}
    finally:
        await asyncio.sleep(0.1)
