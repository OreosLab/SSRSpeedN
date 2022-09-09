import asyncio
import logging
import re

import aiohttp
from aiohttp_socks import ProxyConnector

logger = logging.getLogger("Sub")

# Netflix requestIpAddress regex compile
nf_ip_re = re.compile(r'"requestIpAddress":"(.*)"')


class StreamTest:
    @classmethod
    async def netflix(cls, host, headers, _item, port):
        logger.info(f"Performing netflix test LOCAL_PORT: {port}.")
        try:
            sum_ = 0
            async with aiohttp.ClientSession(
                headers=headers,
                connector=ProxyConnector(host=host, port=port),
                timeout=aiohttp.ClientTimeout(connect=10),
            ) as session:
                async with session.get(
                    url="https://www.netflix.com/title/70242311"
                ) as response1:
                    netflix_ip = "N/A"
                    if response1.status == 200:
                        sum_ += 1
                        netflix_ip = nf_ip_re.findall(str(await response1.read()))[
                            0
                        ].split(",")[0]
                        logger.info("Netflix IP : " + netflix_ip)
                    async with session.get(
                        url="https://www.netflix.com/title/70143836"
                    ) as response2:
                        rg = ""
                        if response2.status == 200:
                            sum_ += 1
                            rg = (
                                f"({str(response2.url).split('com/')[1].split('/')[0]})"
                            )
                        if rg == "(title)":
                            rg = "(us)"
                        # 测试连接状态
                        if sum_ == 0:
                            logger.info("Netflix test result: None.")
                            _item["Ntype"] = "None"
                        elif sum_ == 1:
                            logger.info("Netflix test result: Only Original.")
                            _item["Ntype"] = "Only Original"
                        else:
                            logger.info("Netflix test result: Full DNS.")
                            _item["Ntype"] = "Full DNS" + rg
                        return {"netflix_ip": netflix_ip, "text": f"Full Native{rg}"}
        except Exception as e:
            logger.error("Connect to Netflix exception: " + str(e))
            return {}

    @classmethod
    async def hbomax(cls, host, headers, _item, port):
        logger.info(f"Performing HBO max test LOCAL_PORT: {port}.")
        try:
            async with aiohttp.ClientSession(
                headers=headers,
                connector=ProxyConnector(host=host, port=port),
                timeout=aiohttp.ClientTimeout(connect=10),
            ) as session:
                async with session.get(
                    url="https://www.hbomax.com/", allow_redirects=False
                ) as response:
                    if response.status == 200:
                        _item["Htype"] = True
                    else:
                        _item["Htype"] = False
        except Exception as e:
            logger.error("Connect to HBO max exception: " + str(e))

    @classmethod
    async def disneyplus(cls, host, headers, _item, port):
        logger.info(f"Performing Disney plus test LOCAL_PORT: {port}.")
        try:
            async with aiohttp.ClientSession(
                headers=headers,
                connector=ProxyConnector(host=host, port=port),
                timeout=aiohttp.ClientTimeout(connect=5),
            ) as session:
                async with session.get(
                    url="https://www.disneyplus.com/"
                ) as response1, session.get(
                    url="https://global.edge.bamgrid.com/token"
                ) as response2:
                    if response1.status == 200 and response2.status != 403:
                        text = await response1.text()
                        if text.find("Region", 0, 400) == -1:
                            _item["Dtype"] = False
                        elif response1.history:
                            if 300 <= response1.history[0].status <= 399:
                                _item["Dtype"] = False
                        else:
                            _item["Dtype"] = True
                    else:
                        _item["Dtype"] = False
        except Exception as e:
            logger.error("Connect to Disney plus exception: " + str(e))

    @classmethod
    async def youtube(cls, host, headers, _item, port):
        logger.info(f"Performing Youtube Premium test LOCAL_PORT: {port}.")
        try:
            async with aiohttp.ClientSession(
                headers=headers,
                connector=ProxyConnector(host=host, port=port),
                timeout=aiohttp.ClientTimeout(connect=10),
            ) as session:
                async with session.get(
                    url="https://music.youtube.com/", allow_redirects=False
                ) as response:
                    if "is not available" in await response.text():
                        _item["Ytype"] = False
                    elif response.status == 200:
                        _item["Ytype"] = True
                    else:
                        _item["Ytype"] = False
        except Exception as e:
            logger.error("Connect to Youtube Premium exception: " + str(e))

    @classmethod
    async def abema(cls, host, headers, _item, port):
        logger.info(f"Performing Abema test LOCAL_PORT: {port}.")
        try:
            async with aiohttp.ClientSession(
                headers=headers,
                connector=ProxyConnector(host=host, port=port),
                timeout=aiohttp.ClientTimeout(connect=10),
            ) as session:
                async with session.get(
                    url="https://api.abema.io/v1/ip/check?device=android",
                    allow_redirects=False,
                ) as response:
                    text = await response.text()
                    if text.count("Country") > 0:
                        _item["Atype"] = True
                    else:
                        _item["Atype"] = False
        except Exception as e:
            logger.error("Connect to Abema exception: " + str(e))

    @classmethod
    async def bahamut(cls, host, headers, _item, port):
        logger.info(f"Performing Bahamut test LOCAL_PORT: {port}.")
        try:
            async with aiohttp.ClientSession(
                headers=headers,
                connector=ProxyConnector(host=host, port=port),
                timeout=aiohttp.ClientTimeout(connect=10),
            ) as session:
                async with session.get(
                    url="https://ani.gamer.com.tw/ajax/token.php?adID=89422&sn=14667",
                    allow_redirects=False,
                ) as response:
                    text = await response.text()
                    if text.count("animeSn") > 0:
                        _item["Btype"] = True
                    else:
                        _item["Btype"] = False
        except Exception as e:
            logger.error("Connect to Bahamut exception: " + str(e))

    @classmethod
    async def indazn(cls, host, headers, _item, port):
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
                    if response.status == 200:
                        _item["Dztype"] = True
                    else:
                        _item["Dztype"] = False
        except Exception as e:
            logger.error("Connect to Dazn exception: " + str(e))

    @classmethod
    async def mytvsuper(cls, host, headers, _item, port):
        logger.info(f"Performing TVB test LOCAL_PORT: {port}.")
        try:
            async with aiohttp.ClientSession(
                headers=headers,
                connector=ProxyConnector(host=host, port=port),
                timeout=aiohttp.ClientTimeout(connect=10),
            ) as session:
                async with session.get(
                    url="https://www.mytvsuper.com/iptest.php", allow_redirects=False
                ) as response:
                    text = await response.text()
                    if text.count("HK") > 0:
                        _item["Ttype"] = True
                    else:
                        _item["Ttype"] = False
        except Exception as e:
            logger.error("Connect to TVB exception: " + str(e))

    @classmethod
    async def bilibili(cls, host, headers, _item, port):
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
                            _item["Bltype"] = "台湾"
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
                                        _item["Bltype"] = "港澳台"
                                else:
                                    _item["Bltype"] = "N/A"
        except Exception as e:
            logger.error("Connect to Bilibili exception: " + str(e))


async def run_test_stream(_item, port, get_outbound_info, stream_cfg):
    host = "127.0.0.1"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/64.0.3282.119 Safari/537.36 ",
    }
    test_list = []
    netflix_task = None
    if stream_cfg["HBO_TEST"]:
        test_list.append(
            asyncio.create_task(StreamTest.hbomax(host, headers, _item, port))
        )
    if stream_cfg["DISNEY_TEST"]:
        test_list.append(
            asyncio.create_task(StreamTest.disneyplus(host, headers, _item, port))
        )
    if stream_cfg["YOUTUBE_TEST"]:
        test_list.append(
            asyncio.create_task(StreamTest.youtube(host, headers, _item, port))
        )
    if stream_cfg["ABEMA_TEST"]:
        test_list.append(
            asyncio.create_task(StreamTest.abema(host, headers, _item, port))
        )
    if stream_cfg["BAHAMUT_TEST"]:
        test_list.append(
            asyncio.create_task(StreamTest.bahamut(host, headers, _item, port))
        )
    if stream_cfg["DAZN_TEST"]:
        test_list.append(
            asyncio.create_task(StreamTest.indazn(host, headers, _item, port))
        )
    if stream_cfg["TVB_TEST"]:
        test_list.append(
            asyncio.create_task(StreamTest.mytvsuper(host, headers, _item, port))
        )
    if stream_cfg["BILIBILI_TEST"]:
        test_list.append(
            asyncio.create_task(StreamTest.bilibili(host, headers, _item, port))
        )
    if stream_cfg["NETFLIX_TEST"]:
        netflix_task = asyncio.create_task(
            StreamTest.netflix(host, headers, _item, port)
        )
        test_list.append(netflix_task)
    await asyncio.wait(test_list)
    if netflix_task:
        netflix_result = netflix_task.result()
        if netflix_result.get("netflix_ip", "") == get_outbound_info["outboundGeoIP"]:
            if Ntype := netflix_result.get("text", None):
                logger.info("Netflix test result: Full Native.")
                get_outbound_info["_item"]["Ntype"] = Ntype
