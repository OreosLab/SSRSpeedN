from .ssc import get_config as shadowsocks_get_config
from .trojanc import get_config as trojan_get_config
from .v2rayc import V2RayBaseConfigs

__all__ = ["trojan_get_config", "shadowsocks_get_config", "V2RayBaseConfigs"]
