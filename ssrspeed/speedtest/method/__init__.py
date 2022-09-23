from . import (
    fast,
    speedtestnet,
    st_asyncio,
    st_netflix as stNF,
    st_socket as stSocket,
    st_stream,
    st_ytb as stYtb,
    webpage_simulation,
)
from .ping import google_ping, tcp_ping

__all__ = [
    "fast",
    "speedtestnet",
    "st_asyncio",
    "st_stream",
    "stNF",
    "stSocket",
    "stYtb",
    "webpage_simulation",
    "google_ping",
    "tcp_ping",
]
