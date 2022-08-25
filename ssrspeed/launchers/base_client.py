import logging
import signal
from typing import Any, Dict, Optional

from ssrspeed.config import ssrconfig
from ssrspeed.utils import check_platform

logger = logging.getLogger("Sub")


class BaseClient(object):
    def __init__(self):
        self._localAddress: str = ssrconfig.get("localAddress", "127.0.0.1")
        self._localPort: int = ssrconfig.get("localPort", 1087)
        self._config_list: list = []
        self._config: Dict[str, Any] = {}
        self._platform: str = self._check_platform()
        self._process = None

    @staticmethod
    def _check_platform() -> str:
        return check_platform()

    def _before_stop_client(self):
        pass

    def start_client(self, _config: Dict[str, Any]):
        pass

    def check_alive(self) -> Optional[int]:
        return self._process.poll() is None

    def test_process_terminate(self):
        self._process.terminate()

    # fmt: off
    def stop_client(self):
        self._before_stop_client()
        if self._process is not None:
            if self._check_platform() == "Windows":
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


if __name__ == "__main__":
    pass
