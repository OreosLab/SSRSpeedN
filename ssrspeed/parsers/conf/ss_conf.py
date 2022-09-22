import copy

_shadowsocks_config: dict = {
    "server": "",
    "server_port": -1,
    "method": "",
    "protocol": "",
    "obfs": "",
    "plugin": "",
    "password": "",
    "protocol_param": "",
    "obfsparam": "",
    "plugin_opts": "",
    "plugin_args": "",
    "remarks": "",
    "group": "N/A",
    "timeout": 0,
    "local_port": 0,
    "local_address": "",
    "fastopen": False,
}


def get_config(
    local_address: str = "127.0.0.1", local_port: int = 1087, timeout: int = 10
) -> dict:
    res = copy.deepcopy(_shadowsocks_config)
    res["local_port"] = local_port
    res["local_address"] = local_address
    res["timeout"] = timeout
    return res
