from ssrspeed.launcher.base import BaseClient


class Trojan(BaseClient):
    def __init__(self, clients_dir: str, file: str):
        super().__init__(clients_dir, {"win": "trojan", "unix": "trojan"}, file)
        self._cmd: dict = {
            "win_debug": [
                f"{self._clients_dir}trojan/trojan.exe",
                "--config",
                self._config_file,
            ],
            "win": [
                f"{self._clients_dir}trojan/trojan.exe",
                "--config",
                self._config_file,
            ],
            "unix_debug": [
                f"{self._clients_dir}trojan/trojan",
                "--config",
                self._config_file,
            ],
            "unix": [
                f"{self._clients_dir}trojan/trojan",
                "--config",
                self._config_file,
            ],
        }
