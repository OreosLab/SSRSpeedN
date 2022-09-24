"""
Python CLI-tool (without need for a GUI) to measure Internet speed with fast.com
"""


import contextlib
import json
import socket
import time
import urllib.error
import urllib.request
from threading import Thread

import socks
from loguru import logger


def set_proxy(local_address, local_port):
    socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, local_address, local_port)
    socket.socket = socks.socksocket


def get_html_result(url, result, index):
    """
    get the stuff from url in chunks of size CHUNK,
    and keep writing the number of bytes retrieved into result[index]
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
    """find IPv4 address of fqdn"""
    return socket.getaddrinfo(fqdn, 80, socket.AF_INET)[0][4][0]


def find_ipv6(fqdn):
    """find IPv6 address of fqdn"""
    return socket.getaddrinfo(fqdn, 80, socket.AF_INET6)[0][4][0]


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
        logger.exception("No connection at all")
        # no connection at all?
        return 0
    response = url_result.read().decode().strip()
    for line in response.split("\n"):
        # We're looking for a line like
        #           <script ssrspeed="/app-40647a.js"></script>
        if line.find("script src") >= 0:
            jsname = line.split('"')[1]  # At time of writing: '/app-40647a.js'

    # From that javascript file, get the token:
    url = f"https://fast.com{jsname}"
    if verbose:
        logger.debug(f"javascript url is{url}")
    try:
        url_result = urllib.request.urlopen(url)
    except Exception:
        # connection is broken
        return 0
    all_js_stuff = (
        url_result.read().decode().strip()
    )  # this is an obfuscated Javascript file

    # We're searching for the "token:" in this string:
    # .dummy,DEFAULT_PARAMS={https:!0,token:"YXNkZmFzZGxmbnNkYWZoYXNkZmhrYWxm",urlCount:3,e
    for line in all_js_stuff.split(","):
        if line.find("token:") >= 0:
            if verbose:
                logger.debug(f"line is{line}")
            token = line.split('"')[1]
            if verbose:
                logger.debug(f"token is{token}")
            if token:
                break

    # With the token, get the (3) speed-test-URLS from api.fast.com (which will be in JSON format):
    baseurl = "https://api.fast.com/"
    if force_ipv4:
        # force IPv4 by connecting to an IPv4 address of api.fast.com (over ... HTTP)
        ipv4 = find_ipv4("api.fast.com")
        baseurl = f"http://{ipv4}/"  # HTTPS does not work IPv4 addresses, thus use HTTP
    elif force_ipv6:
        # force IPv6
        ipv6 = find_ipv6("api.fast.com")
        baseurl = f"http://[{ipv6}]/"

    # Not more than 3 possible
    url = f"{baseurl}netflix/speedtest?https=true&token={token}&urlCount=3"
    if verbose:
        logger.debug(f"API url is{url}")
    try:
        url_result = urllib.request.urlopen(url=url, timeout=2)  # 2 second time-out
    except Exception:
        # not good
        if verbose:
            logger.exception(
                "No connection possible"
            )  # probably IPv6, or just no network
        return 0  # no connection, thus no speed

    json_result = url_result.read().decode().strip()
    parsed_json = json.loads(json_result)

    # Prepare for getting those URLs in a threaded way:
    amount = len(parsed_json)
    if verbose:
        logger.debug(f"Number of URLs:{amount}")
    threads = [None] * amount
    results = [0] * amount
    urls = [None] * amount
    for i, json_element in enumerate(parsed_json):
        urls[i] = json_element["url"]  # fill out speed test url from the json format
        if verbose:
            logger.debug(json_element["url"])
    # Let's check whether it's IPv6:
    for url in urls:
        fqdn = url.split("/")[2]
        with contextlib.suppress(Exception):
            socket.getaddrinfo(fqdn, None, socket.AF_INET6)
            if verbose:
                logger.info("IPv6")
    # Now start the threads
    for i, t in enumerate(threads):
        # print("Thread: i is", i)
        t = Thread(target=get_html_result, args=(urls[i], results, i))
        t.daemon = True
        t.start()

    # Monitor the amount of bytes (and speed) of the threads
    time.sleep(1)
    sleep_secs = 3  # 3 seconds sleep
    last_total = 0
    highest_speed_kbps = 0
    nr_loops = int(max_time / sleep_secs)
    for loop in range(nr_loops):
        total = sum(results[i] for i in range(len(threads)))
        delta = total - last_total
        speed_kbps = (delta / sleep_secs) / 1024
        if verbose:
            logger.info(
                f"Loop {loop} Total {total / (1024 * 1024)} MB, "
                f"Delta {delta / (1024 * 1024)} MB, "
                f"Speed {speed_kbps} KB/s "
                f"aka {application_bytes_to_networkbits(speed_kbps) / 1024:.1f} Mbps "
            )
        last_total = total
        if speed_kbps > highest_speed_kbps:
            highest_speed_kbps = speed_kbps
        time.sleep(sleep_secs)

    mbps = round(application_bytes_to_networkbits(highest_speed_kbps) / 1024, 1)
    if verbose:
        logger.info(
            f"Highest Speed (kB/s):{str(highest_speed_kbps)}aka Mbps {str(mbps)}"
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
