# Author: ranwen NyanChan
import asyncio
import socket
import time

from loguru import logger


async def tcp_ping_task(loop, _list, address, port):
    alt = fac = suc = 0
    try:
        sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        sock.settimeout(3)
        current_time = time.time()
        await loop.sock_connect(sock, (address, port))
        sock.close()
        delta_time = time.time() - current_time
        alt += delta_time
        suc += 1
        _list.append(delta_time)
    except socket.timeout:
        fac += 1
        _list.append(0)
        logger.error(f"TCP Ping ({address},{port}) Timeout {fac} times.")
    except ConnectionResetError:
        logger.error("TCP Ping Reset")
        _list.append(0)
        fac += 1
    except ConnectionRefusedError:
        logger.error("TCP Ping RefusedError")
        _list.append(0)
        fac += 1
    except Exception:
        logger.exception("TCP Ping Exception:")
        _list.append(0)
        fac += 1
    return {"alt": alt, "fac": fac, "suc": suc}


async def google_ping_task(loop, _list, address, port):
    alt = fac = suc = 0
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        await loop.sock_connect(sock, (address, port))
        current_time = time.time()
        await loop.sock_sendall(sock, b"\x05\x01\x00")
        await loop.sock_recv(sock, 2)
        await loop.sock_sendall(sock, b"\x05\x01\x00\x03\x0agoogle.com\x00\x50")
        await loop.sock_recv(sock, 10)
        await loop.sock_sendall(
            sock,
            b"GET / HTTP/1.1\r\nHost: google.com\r\nUser-Agent: curl/11.45.14\r\n\r\n",
        )
        await loop.sock_recv(sock, 1)
        sock.close()
        delta_time = time.time() - current_time
        alt += delta_time
        suc += 1
        _list.append(delta_time)
    except socket.timeout:
        fac += 1
        _list.append(0)
        logger.error(f"Google Ping Timeout {fac} times.")
    except Exception:
        logger.exception("Google Ping Exception:")
        _list.append(0)
        fac += 1
    return {"alt": alt, "fac": fac, "suc": suc}


async def tcp_ping(address: str, port: int) -> tuple:
    alt = fac = suc = 0
    loop = asyncio.get_running_loop()
    _list: list = []
    test_ping = [
        asyncio.create_task(tcp_ping_task(loop, _list, address, port)) for _ in range(3)
    ]
    done, _ = await asyncio.wait(test_ping, timeout=5)
    for each in done:
        result = each.result()
        alt += result["alt"]
        fac += result["fac"]
        suc += result["suc"]
    return (0, 0, _list) if suc == 0 else (alt / suc, suc / (suc + fac), _list)


async def google_ping(address: str, port: int) -> tuple:
    alt = fac = suc = 0
    loop = asyncio.get_running_loop()
    _list: list = []
    test_ping = [
        asyncio.create_task(google_ping_task(loop, _list, address, port))
        for _ in range(3)
    ]
    done, _ = await asyncio.wait(test_ping, timeout=5)
    for each in done:
        result = each.result()
        alt += result["alt"]
        fac += result["fac"]
        suc += result["suc"]
    return (0, 0, _list) if suc == 0 else (alt / suc, suc / (suc + fac), _list)


if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    logger.info(asyncio.run(tcp_ping("127.0.0.1", 7890)))
    logger.info(asyncio.run(google_ping("127.0.0.1", 7890)))
