import platform


def check_platform() -> str:
    tmp = platform.platform()
    # print(tmp)
    if "Windows" in tmp:
        return "Windows"
    if "Linux" in tmp:
        return "Linux"
    return "MacOS" if "Darwin" in tmp or "mac" in tmp else "Unknown"


PLATFORM = check_platform()
