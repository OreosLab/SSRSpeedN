import asyncio
import re

import aiohttp
from aiohttp_socks import ProxyConnector
from loguru import logger

# Netflix requestIpAddress regex compile
nf_ip_re = re.compile(r'"requestIpAddress":"(.*)"')


class StreamTest:
    @classmethod
    async def netflix(cls, host, headers, inner_dict, port, outbound_ip):
        logger.info(f"Performing netflix test LOCAL_PORT: {port}.")
        try:
            sum_ = 0
            async with aiohttp.ClientSession(
                headers=headers,
                connector=ProxyConnector(host=host, port=port),
                timeout=aiohttp.ClientTimeout(connect=10),
            ) as session, session.get(
                url="https://www.netflix.com/title/70242311"
            ) as response1:
                netflix_ip = "N/A"
                if response1.status == 200:
                    sum_ += 1
                    netflix_ip = nf_ip_re.findall(str(await response1.read()))[0].split(
                        ","
                    )[0]
                    logger.info(f"Netflix IP : {netflix_ip}")
                async with session.get(
                    url="https://www.netflix.com/title/70143836"
                ) as response2:
                    rg = ""
                    if response2.status == 200:
                        sum_ += 1
                        rg = f"({str(response2.url).split('com/')[1].split('/')[0]})"
                    if rg == "(title)":
                        rg = "(us)"
                    # 测试连接状态
                    if sum_ == 0:
                        logger.info("Netflix test result: None.")
                        inner_dict["Ntype"] = "None"
                    elif sum_ == 1:
                        logger.info("Netflix test result: Only Original.")
                        inner_dict["Ntype"] = "Only Original"
                    elif outbound_ip == netflix_ip:
                        logger.info("Netflix test result: Full Native.")
                        inner_dict["Ntype"] = f"Full Native{rg}"
                    else:
                        logger.info("Netflix test result: Full DNS.")
                        inner_dict["Ntype"] = f"Full DNS{rg}"
        except Exception as e:
            logger.error(f"Netflix error: {str(e)}")
            return {}

    @classmethod
    async def hbomax(cls, host, headers, inner_dict, port):
        logger.info(f"Performing HBO max test LOCAL_PORT: {port}.")
        try:
            async with aiohttp.ClientSession(
                headers=headers,
                connector=ProxyConnector(host=host, port=port),
                timeout=aiohttp.ClientTimeout(connect=10),
            ) as session, session.get(
                url="https://www.hbomax.com/", allow_redirects=False
            ) as response:
                inner_dict["Htype"] = response.status == 200
        except Exception as e:
            logger.error(f"HBO max error: {str(e)}")

    @classmethod
    async def disneyplus(cls, host, headers, inner_dict, port):
        logger.info(f"Performing Disney plus test LOCAL_PORT: {port}.")
        try:
            async with aiohttp.ClientSession(
                headers=headers,
                connector=ProxyConnector(host=host, port=port),
                timeout=aiohttp.ClientTimeout(connect=5),
            ) as session, session.get(
                url="https://www.disneyplus.com/"
            ) as response1, session.get(
                url="https://global.edge.bamgrid.com/token"
            ) as response2:
                if response1.status == 200 and response2.status != 403:
                    text = await response1.text()
                    if text.find("Region", 0, 400) == -1:
                        inner_dict["Dtype"] = False
                    elif response1.history:
                        if 300 <= response1.history[0].status <= 399:
                            inner_dict["Dtype"] = False
                    else:
                        inner_dict["Dtype"] = True
                else:
                    inner_dict["Dtype"] = False
        except Exception as e:
            logger.error(f"Disney plus error: {str(e)}")

    @classmethod
    async def youtube(cls, host, headers, inner_dict, port):
        logger.info(f"Performing Youtube Premium test LOCAL_PORT: {port}.")
        try:
            async with aiohttp.ClientSession(
                headers=headers,
                connector=ProxyConnector(host=host, port=port),
                timeout=aiohttp.ClientTimeout(connect=10),
            ) as session, session.get(
                url="https://music.youtube.com/", allow_redirects=False
            ) as response:
                if "is not available" in await response.text():
                    inner_dict["Ytype"] = False
                elif response.status == 200:
                    inner_dict["Ytype"] = True
                else:
                    inner_dict["Ytype"] = False
        except Exception as e:
            logger.error(f"Youtube Premium error: {str(e)}")

    @classmethod
    async def abema(cls, host, headers, inner_dict, port):
        logger.info(f"Performing Abema test LOCAL_PORT: {port}.")
        try:
            async with aiohttp.ClientSession(
                headers=headers,
                connector=ProxyConnector(host=host, port=port),
                timeout=aiohttp.ClientTimeout(connect=10),
            ) as session, session.get(
                url="https://api.abema.io/v1/ip/check?device=android",
                allow_redirects=False,
            ) as response:
                text = await response.text()
                inner_dict["Atype"] = text.count("Country") > 0
        except Exception as e:
            logger.error(f"Abema error: {str(e)}")

    @classmethod
    async def bahamut(cls, host, headers, inner_dict, port):
        logger.info(f"Performing Bahamut test LOCAL_PORT: {port}.")
        try:
            async with aiohttp.ClientSession(
                headers=headers,
                connector=ProxyConnector(host=host, port=port),
                timeout=aiohttp.ClientTimeout(connect=10),
            ) as session, session.get(
                url="https://ani.gamer.com.tw/ajax/token.php?adID=89422&sn=14667",
                allow_redirects=False,
            ) as response:
                text = await response.text()
                inner_dict["Btype"] = text.count("animeSn") > 0
        except Exception as e:
            logger.error(f"Bahamut error: {str(e)}")

    @classmethod
    async def indazn(cls, host, headers, inner_dict, port):
        logger.info(f"Performing Dazn test LOCAL_PORT: {port}.")
        try:
            async with aiohttp.ClientSession(
                headers=headers,
                connector=ProxyConnector(host=host, port=port, verify_ssl=False),
                timeout=aiohttp.ClientTimeout(connect=10),
            ) as session:
                payload = {
                    "LandingPageKey": "generic",
                    "Languages": "zh-CN,zh,en",
                    "Platform": "web",
                    "PlatformAttributes": {},
                    "Manufacturer": "",
                    "PromoCode": "",
                    "Version": "2",
                }
                async with session.post(
                    url="https://startup.core.indazn.com/misl/v5/Startup",
                    json=payload,
                    allow_redirects=False,
                ) as response:
                    inner_dict["Dztype"] = response.status == 200
        except Exception as e:
            logger.error(f"Dazn error: {str(e)}")

    @classmethod
    async def mytvsuper(cls, host, headers, inner_dict, port):
        logger.info(f"Performing TVB test LOCAL_PORT: {port}.")
        try:
            async with aiohttp.ClientSession(
                headers=headers,
                connector=ProxyConnector(host=host, port=port),
                timeout=aiohttp.ClientTimeout(connect=10),
            ) as session, session.get(
                url="https://www.mytvsuper.com/iptest.php", allow_redirects=False
            ) as response:
                text = await response.text()
                inner_dict["Ttype"] = text.count("HK") > 0
        except Exception as e:
            logger.error(f"TVB error: {str(e)}")

    @classmethod
    async def bilibili(cls, host, headers, inner_dict, port):
        logger.info(f"Performing Bilibili test LOCAL_PORT: {port}.")
        try:
            async with aiohttp.ClientSession(
                headers=headers,
                connector=ProxyConnector(host=host, port=port),
                timeout=aiohttp.ClientTimeout(connect=10),
            ) as session:
                params = {
                    "avid": 50762638,
                    "cid": 100279344,
                    "qn": 0,
                    "type": "",
                    "otype": "json",
                    "ep_id": 268176,
                    "fourk": 1,
                    "fnver": 0,
                    "fnval": 16,
                    "module": "bangumi",
                }
                async with session.get(
                    url="https://api.bilibili.com/pgc/player/web/playurl",
                    params=params,
                    allow_redirects=False,
                ) as response:
                    if response.status == 200:
                        json_data = await response.json()
                        if json_data["code"] == 0:
                            inner_dict["Bltype"] = "台湾"
                        else:
                            params = {
                                "avid": 18281381,
                                "cid": 29892777,
                                "qn": 0,
                                "type": "",
                                "otype": "json",
                                "ep_id": 183799,
                                "fourk": 1,
                                "fnver": 0,
                                "fnval": 16,
                                "module": "bangumi",
                            }
                            session.cookie_jar.clear()
                            async with session.get(
                                url="https://api.bilibili.com/pgc/player/web/playurl",
                                params=params,
                                allow_redirects=False,
                            ) as response2:
                                if response2.status == 200:
                                    json_data2 = await response2.json()
                                    if json_data2["code"] == 0:
                                        inner_dict["Bltype"] = "港澳台"
                                else:
                                    inner_dict["Bltype"] = "N/A"
        except Exception as e:
            logger.error(f"Bilibili error: {str(e)}")


async def start_stream_test(port, stream_cfg, outbound_ip):
    host = "127.0.0.1"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
    }
    test_list = []
    inner_dict = {
        "Ntype": "None",
        "Htype": False,
        "Dtype": False,
        "Ytype": False,
        "Atype": False,
        "Btype": False,
        "Dztype": False,
        "Ttype": False,
        "Bltype": "N/A",
    }
    if stream_cfg["HBO_TEST"]:
        test_list.append(
            asyncio.create_task(StreamTest.hbomax(host, headers, inner_dict, port))
        )
    if stream_cfg["DISNEY_TEST"]:
        test_list.append(
            asyncio.create_task(StreamTest.disneyplus(host, headers, inner_dict, port))
        )
    if stream_cfg["YOUTUBE_TEST"]:
        test_list.append(
            asyncio.create_task(StreamTest.youtube(host, headers, inner_dict, port))
        )
    if stream_cfg["ABEMA_TEST"]:
        test_list.append(
            asyncio.create_task(StreamTest.abema(host, headers, inner_dict, port))
        )
    if stream_cfg["BAHAMUT_TEST"]:
        test_list.append(
            asyncio.create_task(StreamTest.bahamut(host, headers, inner_dict, port))
        )
    if stream_cfg["DAZN_TEST"]:
        test_list.append(
            asyncio.create_task(StreamTest.indazn(host, headers, inner_dict, port))
        )
    if stream_cfg["TVB_TEST"]:
        test_list.append(
            asyncio.create_task(StreamTest.mytvsuper(host, headers, inner_dict, port))
        )
    if stream_cfg["BILIBILI_TEST"]:
        test_list.append(
            asyncio.create_task(StreamTest.bilibili(host, headers, inner_dict, port))
        )
    if stream_cfg["NETFLIX_TEST"]:
        test_list.append(
            asyncio.create_task(
                StreamTest.netflix(host, headers, inner_dict, port, outbound_ip)
            )
        )
    await asyncio.wait(test_list)
    return inner_dict


if __name__ == "__main__":
    STREAM_CFG = {
        "NETFLIX_TEST": True,
        "HBO_TEST": True,
        "DISNEY_TEST": True,
        "YOUTUBE_TEST": True,
        "ABEMA_TEST": True,
        "BAHAMUT_TEST": True,
        "DAZN_TEST": True,
        "TVB_TEST": True,
        "BILIBILI_TEST": True,
    }
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    logger.info(asyncio.run(start_stream_test(7890, STREAM_CFG, "N/A")))
