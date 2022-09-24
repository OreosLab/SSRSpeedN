from ssrspeed.launcher.base import BaseClient


class ShadowsocksR(BaseClient):
    def __init__(self, clients_dir: str, file: str):
        super().__init__(
            clients_dir,
            {"win": "shadowsocksr-libev", "unix": "shadowsocksr-Python"},
            file,
        )
        self._cmd: dict = {
            "win_debug": [
                f"{self._clients_dir}shadowsocksr-libev/ssr-local.exe",
                "-u",
                "-v",
                "-c",
                self._config_file,
            ],
            "win": [
                f"{self._clients_dir}shadowsocksr-libev/ssr-local.exe",
                "-u",
                "-c",
                self._config_file,
            ],
            "unix_debug": [
                "python3",
                f"{self._clients_dir}shadowsocksr/shadowsocks/local.py",
                "-v",
                "-c",
                self._config_file,
            ],
            "unix": [
                "python3",
                f"{self._clients_dir}shadowsocksr/shadowsocks/local.py",
                "-c",
                self._config_file,
            ],
        }
