from ssrspeed.launcher.base import BaseClient


class Hysteria(BaseClient):
    def __init__(self, clients_dir: str, file: str):
        super().__init__(clients_dir, {"win": "hysteria", "unix": "hysteria"}, file)
        self._cmd: dict = {
            "win_debug": [
                f"{self._clients_dir}hysteria/hysteria.exe",
                "-c",
                self._config_file,
            ],
            "win": [
                f"{self._clients_dir}hysteria/hysteria.exe",
                "-c",
                self._config_file,
            ],
            "unix_debug": [
                f"{self._clients_dir}hysteria/hysteria",
                "-c",
                self._config_file,
            ],
            "unix": [f"{self._clients_dir}hysteria/hysteria", "-c", self._config_file],
        }
