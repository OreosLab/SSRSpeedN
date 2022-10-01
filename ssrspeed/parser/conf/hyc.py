import copy

_hysteria_config: dict = {
    "server": "example.com:36712",  # 服务器地址
    "protocol": "wechat-video",  # 留空或 "udp", "wechat-video", "faketcp"
    "up_mbps": 12,  # 最大上传速度 Mbps
    "down_mbps": 62,  # 最大下载速度 Mbps
    "socks5": {
        "listen": "127.0.0.1:1080",  # SOCKS5 监听地址
        "timeout": 300,  # TCP 超时秒数
        "disable_udp": False,  # 禁用 UDP 支持
    },
    "obfs": None,  # 混淆密码
    "auth_str": "",  # 字符串验证密钥
    "alpn": "h3",  # QUIC TLS ALPN
    "server_name": "real.name.com",  # 用于验证服务端证书的 hostname
    "insecure": True,  # 忽略一切证书错误
    "remarks": "N/A",
    "group": "N/A",
}


def get_config(local_address: str = "127.0.0.1", local_port: int = 7890) -> dict:
    res = copy.deepcopy(_hysteria_config)
    res["socks5"]["listen"] = f"{local_address}:{local_port}"
    return res
