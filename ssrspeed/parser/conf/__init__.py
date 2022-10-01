from .hyc import get_config as hysteria_get_config
from .ssc import get_config as shadowsocks_get_config
from .trojanc import get_config as trojan_get_config
from .v2rayc import V2RayBaseConfigs

__all__ = [
    "hysteria_get_config",
    "trojan_get_config",
    "shadowsocks_get_config",
    "V2RayBaseConfigs",
]
