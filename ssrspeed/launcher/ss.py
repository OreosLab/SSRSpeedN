from ssrspeed.launcher.base import BaseClient


class Shadowsocks(BaseClient):
    def __init__(self, clients_dir: str, file: str):
        super().__init__(
            clients_dir, {"win": "shadowsocks-libev", "unix": "shadowsocks-libev"}, file
        )
        self._cmd: dict = {
            "win_debug": [
                f"{self._clients_dir}shadowsocks-libev/ss-local.exe",
                "-u",
                "-v",
                "-c",
                self._config_file,
            ],
            "win": [
                f"{self._clients_dir}shadowsocks-libev/ss-local.exe",
                "-u",
                "-c",
                self._config_file,
            ],
            "unix_debug": [
                f"{self._clients_dir}shadowsocks-libev/ss-local",
                "-u",
                "-v",
                "-c",
                self._config_file,
            ],
            "unix": [
                f"{self._clients_dir}shadowsocks-libev/ss-local",
                "-u",
                "-c",
                self._config_file,
            ],
        }
