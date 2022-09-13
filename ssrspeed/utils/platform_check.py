import platform

from loguru import logger

PLATFORM = None


def check_platform() -> str:
    tmp = platform.platform()
    logger.info(f"Platform Info : {tmp}")
    if "Windows" in tmp:
        return "Windows"
    elif "Linux" in tmp:
        return "Linux"
    elif "Darwin" in tmp or "mac" in tmp:
        return "MacOS"
    else:
        return "Unknown"


if not PLATFORM:
    PLATFORM = check_platform()
