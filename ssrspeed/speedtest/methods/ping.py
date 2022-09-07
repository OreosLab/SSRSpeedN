# Author: ranwen NyanChan

import logging
import socket
import time
from typing import Union

logger = logging.getLogger("Sub")


def tcp_ping(host: str, port: int) -> tuple:
    alt: Union[int, float] = 0
    suc: Union[int, float] = 0
    fac: Union[int, float] = 0
    _list = []
    while True:
        if fac >= 3 or (suc != 0 and fac + suc >= 10):
            break
        # 	logger.debug("fac: {}, suc: {}.".format(fac, suc))
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            st = time.time()
            s.settimeout(3)
            s.connect((host, port))
            s.close()
            delta_time = time.time() - st
            alt += delta_time
            suc += 1
            _list.append(delta_time)
        except socket.timeout:
            fac += 1
            _list.append(0)
            logger.warning("TCP Ping (%s,%d) Timeout %d times." % (host, port, fac))
        # 	print("TCP Ping Timeout %d times." % fac)
        except ConnectionResetError:
            logger.exception("TCP Ping Reset:")
            _list.append(0)
            fac += 1
        except Exception:
            logger.exception("TCP Ping Exception:")
            _list.append(0)
            fac += 1
    if suc == 0:
        return 0, 0, _list
    return alt / suc, suc / (suc + fac), _list


def google_ping(address: str, port: int) -> tuple:
    alt: Union[int, float] = 0
    suc: Union[int, float] = 0
    fac: Union[int, float] = 0
    _list = []
    while True:
        if fac >= 3 or (suc != 0 and fac + suc >= 10):
            break
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(3)
            s.connect((address, port))
            st = time.time()
            s.send(b"\x05\x01\x00")
            s.recv(2)
            s.send(b"\x05\x01\x00\x03\x0agoogle.com\x00\x50")
            s.recv(10)
            s.send(
                b"GET / HTTP/1.1\r\nHost: google.com\r\nUser-Agent: curl/11.45.14\r\n\r\n"
            )
            s.recv(1)
            s.close()
            delta_time = time.time() - st
            alt += delta_time
            suc += 1
            _list.append(delta_time)
        except socket.timeout:
            fac += 1
            _list.append(0)
            logger.warning("Google Ping Timeout %d times." % fac)
        except Exception:
            logger.exception("Google Ping Exception:")
            _list.append(0)
            fac += 1
    if suc == 0:
        return 0, 0, _list
    return alt / suc, suc / (suc + fac), _list
