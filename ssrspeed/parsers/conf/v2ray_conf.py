import copy

V2RayBaseConfig: dict = {
    "remarks": "",
    "group": "N/A",
    "server": "",
    "server_port": "",
    "log": {"access": "", "error": "", "loglevel": "warning"},
    "inbounds": [
        {
            "port": 1087,
            "listen": "127.0.0.1",
            "protocol": "socks",
            "sniffing": {"enabled": True, "destOverride": ["http", "tls"]},
            "settings": {"auth": "noauth", "udp": True, "ip": None, "clients": None},
            "streamSettings": None,
        }
    ],
    "outbounds": [
        {
            "tag": "proxy",
            "protocol": "vmess",
            "settings": {
                "vnext": [
                    {
                        "address": "",
                        "port": 1,
                        "users": [
                            {"id": "", "alterId": 0, "email": "", "security": "auto"}
                        ],
                    }
                ],
                "servers": None,
                "response": None,
            },
            "streamSettings": {
                "network": "",
                "security": "",
                "tlsSettings": {},
                "tcpSettings": {},
                "kcpSettings": {},
                "wsSettings": {},
                "httpSettings": {},
                "quicSettings": {},
            },
            "mux": {"enabled": True},
        },
        {
            "tag": "direct",
            "protocol": "freedom",
            "settings": {"vnext": None, "servers": None, "response": None},
            "streamSettings": {},
            "mux": {},
        },
        {
            "tag": "block",
            "protocol": "blackhole",
            "settings": {"vnext": None, "servers": None, "response": {"type": "http"}},
            "streamSettings": {},
            "mux": {},
        },
    ],
    "dns": {},
    "routing": {"domainStrategy": "IPIfNonMatch", "rules": []},
}

tcpSettingsObject: dict = {
    "connectionReuse": True,
    "header": {
        "type": "http",
        "request": {
            "version": "1.1",
            "method": "GET",
            "path": ["/pathpath"],
            "headers": {
                "Host": ["hosthost.com", "test.com"],
                "User-Agent": [
                    "Mozilla/5.0 (Windows NT 10.0; WOW64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36",
                    "Mozilla/5.0 (iPhone; CPU iPhone OS 10_0_2 like Mac OS X) "
                    "AppleWebKit/601.1 (KHTML, like Gecko) CriOS/53.0.2785.109",
                ],
                "Accept-Encoding": ["gzip, deflate"],
                "Connection": ["keep-alive"],
                "Pragma": "no-cache",
            },
        },
        "response": None,
    },
}

quicSettingsObject: dict = {
    "security": "none",
    "key": "",
    "header": {"type": "none", "request": None, "response": None},
}
httpSettingsObject: dict = {"path": "", "host": ["aes-128-gcm"]}
webSocketSettingsObject: dict = {
    "connectionReuse": True,
    "path": "",
    "headers": {"Host": ""},
}

tlsSettingsObject: dict = {"allowInsecure": True, "serverName": ""}


class V2RayBaseConfigs:
    @staticmethod
    def get_tls_object() -> dict:
        return copy.deepcopy(tlsSettingsObject)

    @staticmethod
    def get_ws_object() -> dict:
        return copy.deepcopy(webSocketSettingsObject)

    @staticmethod
    def get_http_object() -> dict:
        return copy.deepcopy(httpSettingsObject)

    @staticmethod
    def get_tcp_object() -> dict:
        return copy.deepcopy(tcpSettingsObject)

    @staticmethod
    def get_quic_object() -> dict:
        return copy.deepcopy(quicSettingsObject)

    @staticmethod
    def get_config() -> dict:
        return copy.deepcopy(V2RayBaseConfig)

    @staticmethod
    def generate_config(
        config: dict, listen: str = "127.0.0.1", port: int = 1087
    ) -> dict:
        _config = V2RayBaseConfigs.get_config()

        _config["inbounds"][0]["listen"] = listen
        _config["inbounds"][0]["port"] = port

        # Common
        _config["remarks"] = config["remarks"]
        _config["group"] = config.get("group", "N/A")
        _config["server"] = config["server"]
        _config["server_port"] = config["server_port"]

        # stream settings
        stream_settings = _config["outbounds"][0]["streamSettings"]
        stream_settings["network"] = config["network"]
        if config["network"] == "tcp":
            if config["type"] == "http":
                tcp_settings = V2RayBaseConfigs.get_tcp_object()
                tcp_settings["header"]["request"]["path"] = config["path"].split(",")
                tcp_settings["header"]["request"]["headers"]["Host"] = config[
                    "host"
                ].split(",")
                stream_settings["tcpSettings"] = tcp_settings
        elif config["network"] == "ws":
            web_socket_settings = V2RayBaseConfigs.get_ws_object()
            web_socket_settings["path"] = config["path"]
            web_socket_settings["headers"]["Host"] = config["host"]
            for k, v in config.get("headers", {}).items():
                web_socket_settings["headers"][k] = v
            stream_settings["wsSettings"] = web_socket_settings
        elif config["network"] == "h2":
            http_settings = V2RayBaseConfigs.get_http_object()
            http_settings["path"] = config["path"]
            http_settings["host"] = config["host"].split(",")
            stream_settings["httpSettings"] = http_settings
        elif config["network"] == "quic":
            quic_settings = V2RayBaseConfigs.get_quic_object()
            quic_settings["security"] = config["host"]
            quic_settings["key"] = config["path"]
            quic_settings["header"]["type"] = config["type"]
            stream_settings["quicSettings"] = quic_settings

        stream_settings["security"] = config["tls"]
        if config["tls"] == "tls":
            tls_settings = V2RayBaseConfigs.get_tls_object()
            tls_settings["allowInsecure"] = (
                config.get("allowInsecure", "false") == "true"
            )
            tls_settings["serverName"] = config.get("tls-host", "")
            stream_settings["tlsSettings"] = tls_settings

        _config["outbounds"][0]["streamSettings"] = stream_settings

        outbound = _config["outbounds"][0]["settings"]["vnext"][0]
        outbound["address"] = config["server"]
        outbound["port"] = config["server_port"]
        outbound["users"][0]["id"] = config["id"]
        outbound["users"][0]["alterId"] = config["alterId"]
        outbound["users"][0]["security"] = config["security"]
        _config["outbounds"][0]["settings"]["vnext"][0] = outbound
        return _config
