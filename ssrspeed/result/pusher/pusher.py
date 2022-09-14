import requests
from loguru import logger

from ssrspeed.config import ssrconfig

UPLOAD_RESULT = ssrconfig["uploadResult"]
TEST_PNG = ssrconfig["path"]["tmp"] + "test.png"


def push2server(filename: str) -> dict:
    result = {"status": -1, "code": -1}
    try:
        logger.info(f"Pushing {filename} to server.")
        files = {"file": open(filename, "rb")}
        param = {"token": UPLOAD_RESULT["apiToken"], "remark": UPLOAD_RESULT["remark"]}
        rep = requests.post(
            UPLOAD_RESULT["server"], files=files, data=param, timeout=10
        )
        result["status"] = rep.status_code
        if rep.status_code == 200:
            if rep.text == "ok":
                result["code"] = 0
        return result
    except requests.exceptions.Timeout:
        logger.error("Connect to server timeout.")
        return result
    except Exception:
        logger.error("Pushing result to server error.", exc_info=True)
        return result


if __name__ == "__main__":
    print(push2server(TEST_PNG))
