import requests
from loguru import logger


def push2server(filename: str, server: str, token: str, remark: str) -> dict:
    result = {"status": -1, "code": -1}
    try:
        logger.info(f"Pushing {filename} to server.")
        files = {"file": open(filename, "rb")}
        param = {"token": token, "remark": remark}
        rep = requests.post(server, files=files, data=param, timeout=10)
        result["status"] = rep.status_code
        if rep.status_code == 200 and rep.text == "ok":
            result["code"] = 0
        return result
    except requests.exceptions.Timeout:
        logger.error("Connect to server timeout.")
        return result
    except Exception:
        logger.exception("Pushing result to server error.")
        return result
