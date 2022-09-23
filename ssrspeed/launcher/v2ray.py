from ssrspeed.launcher.base import BaseClient


class V2Ray(BaseClient):
    def __init__(self, clients_dir: str, file: str):
        super().__init__(clients_dir, {"win": "v2ray-core", "unix": "v2ray-core"}, file)
        self._cmd: dict = {
            "win_debug": [
                f"{self._clients_dir}v2ray-core/v2ray.exe",
                "--config",
                self._config_file,
            ],
            "win": [
                f"{self._clients_dir}v2ray-core/v2ray.exe",
                "--config",
                self._config_file,
            ],
            "unix_debug": [
                f"{self._clients_dir}v2ray-core/v2ray",
                "--config",
                self._config_file,
            ],
            "unix": [
                f"{self._clients_dir}v2ray-core/v2ray",
                "--config",
                self._config_file,
            ],
        }
