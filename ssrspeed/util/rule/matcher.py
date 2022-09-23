from copy import deepcopy

from loguru import logger


class DownloadRuleMatch:
    def __init__(self, file_download: dict):
        self._config: dict = deepcopy(file_download)
        self._download_links: dict = deepcopy(file_download["downloadLinks"])
        self._download_dict: dict = {
            link["tag"]: (link["link"], link["fileSize"])
            for link in self._download_links
        }

    def _get_download_link(self, tag: str = "") -> tuple:
        if tag in self._download_dict:
            return self._download_dict[tag]
        logger.info(f"No (matched) tag {tag}, using default.")
        return self._download_dict.get("default", ("", ""))

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
                if rule.get("continent", "").strip() in continent:
                    logger.info(f"Continent {continent} matched.")
                    return self._get_download_link(rule["tag"])
        logger.info("Rule not matched, using default.")
        return self._get_download_link()

    def get_url(self, data: dict) -> tuple:
        try:
            if data and not self._config["skipRuleMatch"]:
                return self._check_rule(data)
            return self._get_download_link()
        except Exception:
            logger.exception("")
            return self._get_download_link()
