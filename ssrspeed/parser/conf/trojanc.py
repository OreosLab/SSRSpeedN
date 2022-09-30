import copy

_trojan_config: dict = {
    "run_type": "client",
    "local_addr": "127.0.0.1",
    "local_port": 10870,
    "remote_addr": "example.com",
    "remote_port": 443,
    "password": ["password1"],
    "log_level": 1,
    "ssl": {
        "verify": "true",
        "verify_hostname": "true",
        "cert": "",
        "cipher": "ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:"
        "ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:"
        "ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:"
        "ECDHE-ECDSA-AES256-SHA:ECDHE-ECDSA-AES128-SHA:"
        "ECDHE-RSA-AES128-SHA:ECDHE-RSA-AES256-SHA:"
        "DHE-RSA-AES128-SHA:DHE-RSA-AES256-SHA:"
        "AES128-SHA:AES256-SHA:DES-CBC3-SHA",
        "cipher_tls13": "TLS_AES_128_GCM_SHA256:TLS_CHACHA20_POLY1305_SHA256:TLS_AES_256_GCM_SHA384",
        "sni": "",
        "alpn": ["h2", "http/1.1"],
        "reuse_session": "true",
        "session_ticket": "false",
        "curves": "",
    },
    "tcp": {
        "no_delay": "true",
        "keep_alive": "true",
        "reuse_port": "false",
        "fast_open": "false",
        "fast_open_qlen": 20,
    },
    "websocket": {"enabled": "false", "path": "", "host": ""},
    "group": "N/A",
}


def get_config(local_address: str = "127.0.0.1", local_port: int = 7890) -> dict:
    res = copy.deepcopy(_trojan_config)
    res["local_port"] = local_port
    res["local_address"] = local_address
    return res
