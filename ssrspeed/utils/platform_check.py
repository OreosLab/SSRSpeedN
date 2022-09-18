import platform


def check_platform() -> str:
    tmp = platform.platform()
    # print(tmp)
    if "Windows" in tmp:
        return "Windows"
    if "Linux" in tmp:
        return "Linux"
    if "Darwin" in tmp or "mac" in tmp:
        return "MacOS"
    return "Unknown"


PLATFORM = check_platform()
