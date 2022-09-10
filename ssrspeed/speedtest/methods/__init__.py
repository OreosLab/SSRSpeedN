from . import fast, speedtestnet, st_asyncio
from . import st_netflix as stNF
from . import st_socket as stSocket
from . import st_stream
from . import st_ytb as stYtb
from . import webpage_simulation
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
