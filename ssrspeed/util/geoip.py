import asyncio
import contextlib
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
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
        }
        url = "https://api.ip.sb/geoip"
        async with aiohttp.ClientSession(
            headers=headers,
            connector=ProxyConnector(host="127.0.0.1", port=port),
            timeout=aiohttp.ClientTimeout(connect=10, sock_connect=10, sock_read=10),
        ) as session, session.get(url=url) as response:
            tmp = await response.json()
            logger.info(
                f'Server Country Code : {tmp["country_code"]}, '
                f'Continent Code : {tmp["continent_code"]}, '
                f'ISP : {tmp["organization"]}'
            )
            return (
                True,
                tmp["country_code"],
                tmp["continent_code"],
                tmp["organization"],
            )
    except asyncio.TimeoutError:
        logger.error("Parse location timeout.")
    except Exception as e:
        logger.error(f"Parse location failed: {repr(e)}")
        with contextlib.suppress(Exception):
            logger.error(response.content)
    return False, "DEFAULT", "DEFAULT", "DEFAULT"


def check_ipv4(ip: str) -> bool:
    r = re.compile(r"\b((?:25[0-5]|2[0-4]\d|[01]?\d\d?)(?:(?<!\.)\b|\.)){4}")
    rm = r.match(ip)
    return bool(rm and rm[0] == ip)


def domain2ip(domain: str) -> str:
    logger.info(f"Translating {domain} to ipv4.")
    try:
        return socket.gethostbyname(domain)
    except Exception:
        logger.exception(f"Translate {domain} to ipv4 failed.")
        return "N/A"


async def ip_loc(port):
    try:
        logger.info("Starting Geo IP.")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/105.0.0.0 Safari/537.36"
        }
        url = "https://api.ip.sb/geoip"
        async with aiohttp.ClientSession(
            headers=headers,
            connector=ProxyConnector(host="127.0.0.1", port=port),
            timeout=aiohttp.ClientTimeout(connect=10, sock_connect=10, sock_read=10),
        ) as session, session.get(url=url) as response:
            return await response.json()
    except asyncio.TimeoutError:
        logger.error("Geo IP Timeout.")
        return {}
    except python_socks.ProxyTimeoutError:
        logger.error("Geo IP Proxy Timeout.")
        return {}
    except ConnectionResetError:
        logger.error("Geo IP Reset.")
        return {}
    except python_socks.ProxyConnectionError:
        logger.error("Geo IP Proxy Connection Error.")
        return {}
    except aiohttp.ClientOSError:
        logger.error("Geo IP ClientOSError.")
        return {}
    except aiohttp.ServerDisconnectedError:
        logger.error("Geo IP Server disconnected.")
        return {}
    except aiohttp.ContentTypeError:
        logger.error("Geo IP Connection closed.")
        return {}
    except asyncio.IncompleteReadError:
        logger.error("Geo IP Incomplete Read.")
        return {}
    except Exception:
        logger.exception("Geo IP Failed.")
        try:
            logger.error(response.content)
        except Exception:
            return {}
    finally:
        await asyncio.sleep(0.1)


if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    logger.info(domain2ip("www.google.com"))
    logger.info(asyncio.run(parse_location(7890)))
    logger.info(asyncio.run(ip_loc(7890)))
