import signal
from abc import ABCMeta, abstractmethod
from typing import Any, Dict, List

from loguru import logger

from ssrspeed.config import ssrconfig
from ssrspeed.utils import PLATFORM


class BaseClient(metaclass=ABCMeta):
    _platform = PLATFORM

    def __init__(self):
        self._localAddress: str = ssrconfig.get("localAddress", "127.0.0.1")
        self._localPort: int = ssrconfig.get("localPort", 1087)
        self._config_list: List[Dict[str, Any]] = []
        self._config: Dict[str, Any] = {}
        self._process = None

    @abstractmethod
    def start_client(self, config: Dict[str, Any]):
        pass

    def check_alive(self) -> bool:
        return self._process.poll() is None

    def test_process_terminate(self):
        self._process.terminate()

    def _before_stop_client(self):
        pass

    # fmt: off
    def stop_client(self):
        self._before_stop_client()
        if self._process is not None:
            if BaseClient._platform == "Windows":
                self._process.terminate()
            # 	self._process.send_signal(signal.SIGINT)
            else:
                self._process.send_signal(signal.SIGINT)
            # 	self._process.send_signal(signal.SIGQUIT)
        # 	print(self.__process.returncode)
            self._process = None
            logger.info("Client terminated.")
    #   self.__ssrProcess.terminate()
    # fmt: on
