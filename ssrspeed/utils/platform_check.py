import platform

PLATFORM = None


def check_platform() -> str:
    tmp = platform.platform()
    if "Windows" in tmp:
        return "Windows"
    if "Linux" in tmp:
        return "Linux"
    if "Darwin" in tmp or "mac" in tmp:
        return "MacOS"
    return "Unknown"


if not PLATFORM:
    PLATFORM = check_platform()
