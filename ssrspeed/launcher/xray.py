from ssrspeed.launcher.base import BaseClient


class XRay(BaseClient):
    def __init__(self, clients_dir: str, file: str):
        super().__init__(clients_dir, {"win": "xray-core", "unix": "xray-core"}, file)
        self._cmd: dict = {
            "win_debug": [
                f"{self._clients_dir}xray-core/xray.exe",
                "--config",
                self._config_file,
            ],
            "win": [
                f"{self._clients_dir}xray-core/xray.exe",
                "--config",
                self._config_file,
            ],
            "unix_debug": [
                f"{self._clients_dir}xray-core/xray",
                "--config",
                self._config_file,
            ],
            "unix": [
                f"{self._clients_dir}xray-core/xray",
                "--config",
                self._config_file,
            ],
        }
