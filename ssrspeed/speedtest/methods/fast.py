"""
Python CLI-tool (without need for a GUI) to measure Internet speed with fast.com
"""

import json
import socket
import time
import urllib.error
import urllib.parse
import urllib.request
from threading import Thread

import socks
from loguru import logger


def set_proxy(local_address, local_port):
    socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, local_address, local_port)
    socket.socket = socks.socksocket


"""
proxy = {"http":"http://127.0.0.1:1081"}
proxySupport = urllib.request.ProxyHandler({"http":"http://127.0.0.1:1081"})
opener = urllib.request.build_opener(proxySupport)
urllib.request.install_opener(opener)
"""


def get_html_result(url, result, index):
    """
    get the stuff from url in chunks of size CHUNK, and keep writing the number of bytes retrieved into result[index]
    """
    try:
        req = urllib.request.urlopen(url)
    except urllib.error.URLError:
        result[index] = 0
        return
    CHUNK = 100 * 1024
    i = 1
    while True:
        chunk = req.read(CHUNK)
        if not chunk:
            break
        result[index] = i * CHUNK
        i += 1


def application_bytes_to_networkbits(bytes_):
    # convert bytes (at application layer) to bits (at network layer)
    return bytes_ * 8 * 1.0415
    # 8 for bits versus bytes
    # 1.0416 for application versus network layers


def find_ipv4(fqdn):
    """
    find IPv4 address of fqdn
    """
    import socket

    ipv4 = socket.getaddrinfo(fqdn, 80, socket.AF_INET)[0][4][0]
    return ipv4


def find_ipv6(fqdn):
    """
    find IPv6 address of fqdn
    """
    import socket

    ipv6 = socket.getaddrinfo(fqdn, 80, socket.AF_INET6)[0][4][0]
    return ipv6


def fast_com(verbose=False, max_time=15, force_ipv4=False, force_ipv6=False):
    """
    verbose: print debug output
    max_time: max time in seconds to monitor speedtest
    force_ipv4: force speed test over IPv4
    force_ipv6: force speed test over IPv6
    """
    # go to fast.com to get the javascript file
    url = "https://fast.com/"
    try:
        url_result = urllib.request.urlopen(url)
    except Exception:
        logger.error("No connection at all", exc_info=True)
        # no connection at all?
        return 0
    response = url_result.read().decode().strip()
    for line in response.split("\n"):
        # We're looking for a line like
        #           <script ssrspeed="/app-40647a.js"></script>
        if line.find("script src") >= 0:
            jsname = line.split('"')[1]  # At time of writing: '/app-40647a.js'

    # From that javascript file, get the token:
    url = "https://fast.com" + jsname
    if verbose:
        logger.debug("javascript url is" + url)
    try:
        url_result = urllib.request.urlopen(url)
    except Exception:
        # connection is broken
        return 0
    all_js_stuff = (
        url_result.read().decode().strip()
    )  # this is an obfuscated Javascript file

    """
    We're searching for the "token:" in this string:
    .dummy,DEFAULT_PARAMS={https:!0,token:"YXNkZmFzZGxmbnNkYWZoYXNkZmhrYWxm",urlCount:3,e
    """
    for line in all_js_stuff.split(","):
        if line.find("token:") >= 0:
            if verbose:
                logger.debug("line is" + line)
            token = line.split('"')[1]
            if verbose:
                logger.debug("token is" + token)
            if token:
                break

    # With the token, get the (3) speed-test-URLS from api.fast.com (which will be in JSON format):
    baseurl = "https://api.fast.com/"
    if force_ipv4:
        # force IPv4 by connecting to an IPv4 address of api.fast.com (over ... HTTP)
        ipv4 = find_ipv4("api.fast.com")
        baseurl = (
            "http://" + ipv4 + "/"
        )  # HTTPS does not work IPv4 addresses, thus use HTTP
    elif force_ipv6:
        # force IPv6
        ipv6 = find_ipv6("api.fast.com")
        baseurl = "http://[" + ipv6 + "]/"

    url = (
        baseurl + "netflix/speedtest?https=true&token=" + token + "&urlCount=3"
    )  # Not more than 3 possible
    if verbose:
        logger.debug("API url is" + url)
    try:
        url_result = urllib.request.urlopen(url=url, timeout=2)  # 2 second time-out
    except Exception:
        # not good
        if verbose:
            logger.error(
                "No connection possible", exc_info=True
            )  # probably IPv6, or just no network
        return 0  # no connection, thus no speed

    json_result = url_result.read().decode().strip()
    parsed_json = json.loads(json_result)

    # Prepare for getting those URLs in a threaded way:
    amount = len(parsed_json)
    if verbose:
        logger.debug("Number of URLs:" + str(amount))
    threads = [None] * amount
    results = [0] * amount
    urls = [None] * amount
    i = 0
    for json_element in parsed_json:
        urls[i] = json_element["url"]  # fill out speed test url from the json format
        if verbose:
            logger.debug(json_element["url"])
        i += 1

    # Let's check whether it's IPv6:
    for url in urls:
        fqdn = url.split("/")[2]
        try:
            socket.getaddrinfo(fqdn, None, socket.AF_INET6)
            if verbose:
                logger.info("IPv6")
        except Exception:
            pass

    # Now start the threads
    for i in range(len(threads)):
        # print("Thread: i is", i)
        threads[i] = Thread(target=get_html_result, args=(urls[i], results, i))
        threads[i].daemon = True
        threads[i].start()

    # Monitor the amount of bytes (and speed) of the threads
    time.sleep(1)
    sleep_secs = 3  # 3 seconds sleep
    last_total = 0
    highest_speed_kbps = 0
    nr_loops = int(max_time / sleep_secs)
    for loop in range(nr_loops):
        total = 0
        for i in range(len(threads)):
            # print(i, results[i])
            total += results[i]
        delta = total - last_total
        speed_kbps = (delta / sleep_secs) / 1024
        if verbose:
            """
            logger.info(
                "Loop" + loop + "Total MB",
                total / (1024 * 1024),
                "Delta MB",
                delta / (1024 * 1024),
                "Speed kB/s:",
                speed_kbps,
                "aka Mbps %.1f" % (application_bytes_to_networkbits(speed_kbps) / 1024),
            )
            """
            logger.info(
                "Loop %s Total %s MB,Delta %s MB,Speed %s KB/s aka %.1f Mbps"
                % (
                    str(loop),
                    str(total / (1024 * 1024)),
                    str(delta / (1024 * 1024)),
                    str(speed_kbps),
                    application_bytes_to_networkbits(speed_kbps) / 1024,
                )
            )
        last_total = total
        if speed_kbps > highest_speed_kbps:
            highest_speed_kbps = speed_kbps
        time.sleep(sleep_secs)

    mbps = application_bytes_to_networkbits(highest_speed_kbps) / 1024
    mbps = float("%.1f" % mbps)
    if verbose:
        logger.info(
            "Highest Speed (kB/s):" + str(highest_speed_kbps) + "aka Mbps " + str(mbps)
        )

    return mbps


if __name__ == "__main__":
    # 	print("let's speed test:")
    # 	print("\nSpeed test, without logging:")
    # 	print(fast_com())
    # 	print("\nSpeed test, with logging:")
    print(fast_com(verbose=True))
    # 	print("\nSpeed test, IPv4, with verbose logging:")
    # 	print(fast_com(verbose=True, max_time=18, force_ipv4=True))
    # 	print("\nSpeed test, IPv6:")
    # 	print(fast_com(max_time=12, force_ipv6=True))
    # 	fast_com(verbose=True, max_time=25)

    # 	print("\ndone")
