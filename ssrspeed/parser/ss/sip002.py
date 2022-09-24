import binascii
import copy
from typing import Optional
from urllib.parse import parse_qsl, unquote, urlparse

from loguru import logger

from ssrspeed.util import b64plus


class ParserShadowsocksSIP002:
    def __init__(self, base_config: dict):
        self.__config_list: list = []
        self.__base_config: dict = base_config

    def __get_shadowsocks_base_config(self) -> dict:
        return copy.deepcopy(self.__base_config)

    def __parse_link(self, link: str) -> Optional[dict]:
        if not link.startswith("ss://"):
            logger.error(f"Not shadowsocks URL : {link}")
            return None

        ori_url = urlparse(unquote(link))
        netloc = ori_url.netloc
        try:
            _netloc = b64plus.decode(netloc).decode("utf-8")
        except binascii.Error:
            at_pos = netloc.find("@")
            _netloc = b64plus.decode(netloc[:at_pos]).decode("utf-8") + netloc[at_pos:]

        url = ori_url._replace(netloc=_netloc)
        hostname = url.hostname
        port = url.port
        encryption = _netloc.split("@")[0]

        query = dict(parse_qsl(url.query, separator=";"))
        plugin = ""
        plugin_opts = ""
        if query.get("plugin", "").lower() in ["simple-obfs", "obfs-local"]:
            plugin = "simple-obfs"
            if mode := query.get("obfs"):
                plugin_opts += f"obfs={mode}"
            if host := query.get("obfs-host"):
                plugin_opts += f";obfs-host={host}"
        elif query.get("plugin"):
            logger.warning(f"Unsupported plugin: {plugin}.")
            return None

        _config = self.__get_shadowsocks_base_config()
        _config["server"] = hostname
        _config["server_port"] = port
        _config["method"] = encryption.split(":")[0]
        _config["password"] = encryption.split(":")[1]
        _config["remarks"] = url.fragment or hostname
        _config["plugin"] = plugin
        _config["plugin_opts"] = plugin_opts
        return _config

    def parse_single_link(self, link: str) -> Optional[dict]:
        return self.__parse_link(link)

    def parse_subs_config(self, links: list) -> list:
        for link in links:
            link = link.strip()
            if cfg := self.__parse_link(link):
                self.__config_list.append(cfg)

        logger.info(f"Read {len(self.__config_list)} config(s).")
        return self.__config_list


if __name__ == "__main__":
    parser = ParserShadowsocksSIP002({})
    LINKS = "c3M6Ly9ZMmhoWTJoaE1qQXRhV1YwWmkxd2IyeDVNVE13TlRwSElYbENkMUJYU0ROV1lXOUFNVGsyTGpJME55NDFPUzR4TlRRNk9EQXcj8J+HqPCfh6YgQ0FfMDYgfDUxLjc2TWIKc3M6Ly9ZV1Z6TFRJMU5pMW5ZMjA2VkVWNmFtWkJXWEV5U1dwMGRXOVRRREUwT1M0eU1ESXVPREl1TVRjeU9qWTJPVGM9I/Cfh6vwn4e3IEZSXzE2CnNzOi8vWVdWekxUSTFOaTFuWTIwNmEwUlhkbGhaV205VVFtTkhhME0wUURFME5TNHlNemt1TVM0eE1EQTZPRGc0TWc9PSPwn4er8J+HtyBGUl8xNyB8MzAuNjJNYgpzczovL1lXVnpMVEkxTmkxblkyMDZXVFpTT1hCQmRIWjRlSHB0UjBOQU1UUTFMakl6T1M0eExqRXdNRG80T0RnNCPwn4er8J+HtyBGUl8xOCB8MTcuNzFNYgpzczovL1lXVnpMVEkxTmkxblkyMDZabUZDUVc5RU5UUnJPRGRWU2tjM1FERTVOUzR4TlRRdU1qQXdMakUxTURveU16YzIj8J+Hq/Cfh7cgRlJfMTkKc3M6Ly9ZV1Z6TFRJMU5pMW5ZMjA2UzJsNFRIWkxlbmRxWld0SE1EQnliVUF4TkRVdU1qTTVMakV1TVRBd09qZ3dPREE9I/Cfh6vwn4e3IEZSXzIwIHwxOS4zME1iCnNzOi8vWVdWekxUSTFOaTFuWTIwNlMybDRUSFpMZW5kcVpXdEhNREJ5YlVBeE5Ea3VNakF5TGpneUxqRTNNam80TURndyPwn4er8J+HtyBGUl8yMQpzczovL1lXVnpMVEV5T0MxblkyMDZjMmhoWkc5M2MyOWphM05BTWpFeUxqRXdNaTQxTXk0NE1UbzBORE09I/Cfh6zwn4enIEdCXzIyIHwxMi4yOE1iCnNzOi8vWTJoaFkyaGhNakF0YVdWMFppMXdiMng1TVRNd05UcEhJWGxDZDFCWFNETldZVzlBTnpndU1USTVMakkxTXk0NU9qZ3dPUT09I/Cfh6zwn4enIEdCXzIzIHw3Ni4xN01iCnNzOi8vWVdWekxURXlPQzFuWTIwNmMyaGhaRzkzYzI5amEzTkFNakV5TGpFd01pNDFNeTR4T1RjNk5EUXoj8J+HrPCfh6cgR0JfMjQgfDEzLjMxTWIKc3M6Ly9ZV1Z6TFRFeU9DMW5ZMjA2YzJoaFpHOTNjMjlqYTNOQU1qRXlMakV3TWk0MU15NDNPRG8wTkRNPSPwn4es8J+HpyBHQl8yNSB8MTQuMDNNYgpzczovL1lXVnpMVEV5T0MxblkyMDZjMmhoWkc5M2MyOWphM05BTWpFeUxqRXdNaTQxTXk0eE9UUTZORFF6I/Cfh6zwn4enIEdCXzI2IHwxNC4xMU1iCnNzOi8vWTJoaFkyaGhNakF0YVdWMFppMXdiMng1TVRNd05UbzFOVGsxWmpGalppMWtOMk13TFRReE1qRXRZVE5pWmkweE9XVTBNak5qTVdZNVlURkFiV1l3TWk1NGJYTnpMblpwY0RveE9EZzRPQT09I/Cfh7fwn4e6IFJVXzM5IHwxOC40ME1iCnNzOi8vWTJoaFkyaGhNakF0YVdWMFppMXdiMng1TVRNd05Ub3BNVTR4UlRaMk1GTlZYM0pIVkhCblFEYzVMakV6TXk0eE1Ea3VOVFk2TVRBek5nPT0j8J+Ht/Cfh7ogUlVfNDAgfDYyLjI4TWIKc3M6Ly9ZV1Z6TFRJMU5pMW5ZMjA2UzJsNFRIWkxlbmRxWld0SE1EQnliVUF4TnpJdU9Ua3VNVGt3TGpNNU9qVTFNREE9I/Cfh7rwn4e4IFVTXzQ3IHwxNy41ME1iCnNzOi8vWVdWekxUSTFOaTFuWTIwNlp6Vk5aVVEyUm5RelExZHNTa2xrUURFM01pNDVPUzR4T1RBdU16azZOVEF3TXc9PSPwn4e68J+HuCBVU180OCB8MTguMTFNYgpzczovL1lXVnpMVEkxTmkxblkyMDZZMlJDU1VSV05ESkVRM2R1WmtsT1FETTRMakUwTXk0Mk5pNDVPVG80TVRFNCPwn4e68J+HuCBVU180OSB8MTguMDZNYgpzczovL1lXVnpMVEkxTmkxblkyMDZZMlJDU1VSV05ESkVRM2R1WmtsT1FETTRMakV5TVM0ME15NDNNVG80TVRFNSPwn4e68J+HuCBVU181MCB8MjYuODdNYgpzczovL1lXVnpMVEkxTmkxblkyMDZTMmw0VEhaTGVuZHFaV3RITURCeWJVQXhOamN1T0RndU5qRXVNVGMxT2pnd09EQT0j8J+HuvCfh7ggVVNfNTEgfDE5LjQ2TWIKc3M6Ly9ZV1Z6TFRJMU5pMW5ZMjA2YTBSWGRsaFpXbTlVUW1OSGEwTTBRRE00TGpFeU1TNDBNeTQzTVRvNE9EZ3kj8J+HuvCfh7ggVVNfNTIgfDI4LjU1TWIKc3M6Ly9ZV1Z6TFRJMU5pMW5ZMjA2V1RaU09YQkJkSFo0ZUhwdFIwTkFNVFkzTGpnNExqWXpMamM1T2pNek1EWT0j8J+HuvCfh7ggVVNfNTMgfDM0LjUzTWIKc3M6Ly9ZV1Z6TFRJMU5pMW5ZMjA2VkVWNmFtWkJXWEV5U1dwMGRXOVRRRE00TGpZNExqRXpOQzQ0TlRvMk5qYzUj8J+HuvCfh7ggVVNfNTQgfDE1LjcyTWIKc3M6Ly9ZV1Z6TFRJMU5pMW5ZMjA2UzJsNFRIWkxlbmRxWld0SE1EQnliVUF6T0M0Mk5DNHhNemd1TVRRMU9qZ3dPREE9I/Cfh7rwn4e4IFVTXzU1IHw2MC4yME1iCnNzOi8vWVdWekxUSTFOaTFuWTIwNldUWlNPWEJCZEhaNGVIcHRSME5BTXpndU5qZ3VNVE0wTGpnMU9qVTJNREE9I/Cfh7rwn4e4IFVTXzU2IHwgNy44ME1iCnNzOi8vWVdWekxUSTFOaTFuWTIwNldUWlNPWEJCZEhaNGVIcHRSME5BTXpndU1UUXpMalkyTGprNU9qVXdNREU9I/Cfh7rwn4e4IFVTXzU3IHwyNS42Mk1iCnNzOi8vWVdWekxUSTFOaTFuWTIwNlp6Vk5aVVEyUm5RelExZHNTa2xrUURNNExqa3hMakV3TWk0M05EbzFNREF6I/Cfh7rwn4e4IFVTXzU4IHw0MS45Mk1iCnNzOi8vWVdWekxUSTFOaTFuWTIwNlZFVjZhbVpCV1hFeVNXcDBkVzlUUURNNExqRXhOQzR4TVRRdU5qYzZOalk1Tnc9PSPwn4e68J+HuCBVU181OSB8MTAuODJNYgpzczovL1lXVnpMVEkxTmkxblkyMDZTMmw0VEhaTGVuZHFaV3RITURCeWJVQXpPQzQzTlM0eE16WXVNakU2T0RBNE1BPT0j8J+HuvCfh7ggVVNfNjAgfCA4LjM2TWIKc3M6Ly9ZV1Z6TFRJMU5pMW5ZMjA2V1RaU09YQkJkSFo0ZUhwdFIwTkFNemd1TVRFMExqRXhOQzR4T1RvMU5qQXgj8J+HuvCfh7ggVVNfNjEgfDIwLjE2TWIKc3M6Ly9ZV1Z6TFRJMU5pMW5ZMjA2V1RaU09YQkJkSFo0ZUhwdFIwTkFNemd1TnpVdU1UTTJMakl4T2pVd01ERT0j8J+HuvCfh7ggVVNfNjIgfDE0LjE0TWIKc3M6Ly9ZV1Z6TFRJMU5pMW5ZMjA2Y0V0RlZ6aEtVRUo1VkZaVVRIUk5RRE00TGpFeE5DNHhNVFF1TVRrNk5EUXoj8J+HuvCfh7ggVVNfNjMgfDMyLjY2TWIKc3M6Ly9ZV1Z6TFRJMU5pMW5ZMjA2WnpWTlpVUTJSblF6UTFkc1NrbGtRRE00TGpjMUxqRXpOaTR5TVRvMU1EQXoj8J+HuvCfh7ggVVNfNjQgfDEyLjI0TWIKc3M6Ly9ZV1Z6TFRFeU9DMWpabUk2YzJoaFpHOTNjMjlqYTNOQU1UVTJMakUwTmk0ek9DNHhOak02TkRReiPwn4e68J+HuCBVU182NSB8MTUzLjI5TWIKc3M6Ly9ZV1Z6TFRJMU5pMW5ZMjA2UzJsNFRIWkxlbmRxWld0SE1EQnliVUF6T0M0Mk9DNHhNelV1TVRnNk5UVXdNQT09I/Cfh7rwn4e4IFVTXzY2IHwxNS4wOE1iCnNzOi8vWTJoaFkyaGhNakF0YVdWMFppMXdiMng1TVRNd05UcEhJWGxDZDFCWFNETldZVzlBTVRNMExqRTVOUzR4T1RZdU1UYzRPamd3TkE9PSPwn4+BIFpaXzEwNiB8MTUzLjAxTWIKc3M6Ly9ZMmhoWTJoaE1qQXRhV1YwWmkxd2IyeDVNVE13TlRwSElYbENkMUJYU0ROV1lXOUFNVE0wTGpFNU5TNHhPVFl1TVRRek9qZ3dOUT09I/Cfj4EgWlpfMTA3IHwxMzUuNDFNYgpzczovL1lXVnpMVEkxTmkxblkyMDZSbTlQYVVkc2EwRkJPWGxRUlVkUVFERXpOQzR4T1RVdU1UazJMakUwT1RvM016QTMj8J+PgSBaWl8xMDggfDU5Ljc0TWIKc3M6Ly9ZV1Z6TFRJMU5pMW5ZMjA2Um05UGFVZHNhMEZCT1hsUVJVZFFRREUyT1M0eE9UY3VNVFF6TGpJek1qbzNNekEzI/Cfj4EgWlpfMTA5IHw0NS4wNk1iCg=="
    for i in b64plus.decode(LINKS).decode("utf-8").splitlines():
        print(parser.parse_single_link(i))
    LINK = "ss://cmM0LW1kNTpwYXNzd2Q=@192.168.100.1:8888/?plugin=obfs-local%3Bobfs%3Dhttp#Example2"
    print(parser.parse_single_link(LINK))
