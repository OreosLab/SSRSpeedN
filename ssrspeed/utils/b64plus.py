import base64


def fill_b64(data: str) -> str:
    if len(data) % 4:
        data += "=" * (4 - (len(data) % 4))
    return data


def _url_safe_decode(s: str) -> bytes:
    s = fill_b64(s)
    s = s.replace("-", "+").replace("_", "/")
    return base64.b64decode(s, validate=True)


def encode(s: str) -> bytes:
    return base64.urlsafe_b64encode(s.encode("utf-8"))


def decode(s: str) -> bytes:
    return _url_safe_decode(s)
