from copy import deepcopy

from loguru import logger

from ssrspeed.config import ssrconfig


class DownloadRuleMatch:
    def __init__(self):
        self._config: dict = deepcopy(ssrconfig["fileDownload"])
        self._download_links: dict = deepcopy(self._config["downloadLinks"])

    def _get_download_link(self, tag: str = "") -> tuple:
        default: tuple = tuple()
        for link in self._download_links:
            if link["tag"] == "Default":
                default = (link["link"], link["fileSize"])
        if not tag:
            logger.info("No tag, using default.")
            return default
        for link in self._download_links:
            if link["tag"] == tag:
                logger.info(f"Tag matched: {tag}")
                return link["link"], link["fileSize"]
        logger.info(f"Tag {tag} not matched, using default.")
        return default

    def _check_rule(self, data: dict) -> tuple:
        isp = data["organization"].strip()
        country_code = data["country_code"].strip()
        continent = data["continent_code"].strip()
        rules = self._config["rules"]
        for rule in rules:
            if rule["mode"].lower() == "match_isp":
                logger.debug("Match mode: ISP")
                if isp in rule["ISP"].strip():
                    logger.info(f"ISP {isp} matched.")
                    return self._get_download_link(rule["tag"])
            elif rule["mode"].lower() == "match_location":
                logger.debug("Match mode: Location")
                for code in rule.get("countries", []):
                    if country_code == code.strip():
                        logger.info(f"Country {code} matched.")
                        return self._get_download_link(rule["tag"])
                if (
                    rule.get("continent", "") != ""
                    and rule["continent"].strip() in continent
                ):
                    logger.info(f"Continent {continent} matched.")
                    return self._get_download_link(rule["tag"])
        logger.info("Rule not matched, using default.")
        return self._get_download_link()

    def get_url(self, data: dict) -> tuple:
        try:
            if data and not self._config["skipRuleMatch"]:
                return self._check_rule(data)
            else:
                return self._get_download_link()
        except Exception:
            logger.error("", exc_info=True)
            return self._get_download_link()
