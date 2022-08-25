import logging
import platform

logger = logging.getLogger("Sub")


def check_platform() -> str:
    tmp = platform.platform()
    logger.info("Platform Info : {}".format(str(tmp)))
    if "Windows" in tmp:
        return "Windows"
    elif "Linux" in tmp:
        return "Linux"
    elif "Darwin" in tmp or "mac" in tmp:
        return "MacOS"
    else:
        return "Unknown"
