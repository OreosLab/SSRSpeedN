import asyncio.exceptions
import logging
import re
import socket

import aiohttp
import python_socks
from aiohttp_socks import ProxyConnector

logger = logging.getLogger("Sub")


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
                    "Server Country Code : %s,Continent Code : %s,ISP : %s"
                    % (tmp["country_code"], tmp["continent_code"], tmp["organization"])
                )
            return True, tmp["country_code"], tmp["continent_code"], tmp["organization"]
    except asyncio.TimeoutError:
        logger.error("Parse location timeout.")
    except:
        logger.exception("Parse location failed.")
        try:
            logger.error(response.content)
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


async def ip_loc(port):
    try:
        """
        if ip != "" and not check_ipv4(ip):
            logger.error("Invalid IP : {}".format(ip))
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
    except python_socks.ProxyTimeoutError:
        logger.error("Geo IP Proxy Timeout.")
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
    except:
        logger.exception("Geo IP Failed.")
        try:
            logger.error(response.content)
        except:
            return {}
    finally:
        await asyncio.sleep(0.1)
