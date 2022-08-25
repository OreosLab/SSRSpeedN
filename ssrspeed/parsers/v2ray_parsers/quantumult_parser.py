import logging
from typing import Optional

from ssrspeed.utils import b64plus

logger = logging.getLogger("Sub")


class ParserV2RayQuantumult(object):
    def __init__(self):
        pass

    @staticmethod
    def parse_subs_config(raw_link: str) -> Optional[dict]:
        link = raw_link[8:]
        link_decoded = b64plus.decode(link).decode("utf-8")
        try:
            link_splited = link_decoded.split(",")

            new_list = []
            while True:
                try:
                    item = link_splited.pop(0)
                except IndexError:
                    break
                text = item
                while text.count('"') % 2 != 0:
                    try:
                        text += ", {}".format(link_splited.pop(0))
                    except IndexError:
                        raise ValueError("Invalid Quantumult URL.")
                new_list.append(text)
            link_splited = new_list

            remarks = link_splited[0].split(" = ")[0]
            server = link_splited[1]
            remarks = remarks if remarks else server
            port = int(link_splited[2])
            security = link_splited[3]
            uuid = link_splited[4].replace('"', "")
            group = link_splited[5].split("=")[1]
            tls = ""
            tls_host = ""
            host = ""  # http host, web socket host, h2 host, quic encrypt method
            net = "tcp"
            path = ""  # Websocket path, http path, quic encrypt key
            headers = []

            if link_splited[6].split("=")[1] == "true":
                tls = "tls"
                tls_host = link_splited[7].split("=")[1]
                allow_insecure = (
                    False if (link_splited[8].split("=")[1] == "1") else True
                )
            else:
                allow_insecure = True
            i = 7
            if tls:
                i = 8
            if len(link_splited) == 11 or len(link_splited) == 12:
                net = link_splited[i + 1].split("=")[1]
                path = link_splited[i + 2].split("=")[1].replace('"', "")
                header = (
                    link_splited[i + 3].split("=")[1].replace('"', "").split("[Rr][Nn]")
                )
                if len(header) > 0:
                    host = header[0].split(":")[1].strip()
                    for h in range(1, len(header)):
                        headers.append(
                            {
                                "header": header[h].split(":")[0].strip(),
                                "value": header[h].split(":")[1].strip(),
                            }
                        )

            _type = "none"  # Obfs type under tcp mode
            aid = 0
            logger.debug(
                "Server : {}, Port : {}, tls-host : {}, Path : {}, Type : {}, UUID : {}, AlterId : {}, Network : {}, "
                "Host : {}, Headers : {}, TLS : {}, Remarks : {}, group={}".format(
                    server,
                    port,
                    tls_host,
                    path,
                    _type,
                    uuid,
                    aid,
                    net,
                    host,
                    headers,
                    tls,
                    remarks,
                    group,
                )
            )
            _config = {
                "remarks": remarks,
                "group": group,
                "server": server,
                "server_port": port,
                "id": uuid,
                "alterId": aid,
                "security": security,
                "allowInsecure": allow_insecure,
                "type": _type,
                "path": path,
                "network": net,
                "host": host,
                "headers": headers,
                "tls": tls,
                "tls-host": tls_host,
            }
            return _config
        except:
            logger.exception("Parse {} failed. (Quantumult Method)".format(raw_link))
            return None
