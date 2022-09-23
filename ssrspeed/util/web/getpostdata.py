import json
import urllib.parse

from flask import request

from ssrspeed.util.web.parseqsplus import parse_qs_plus


def get_post_data() -> dict:
    # print(request.content_type)
    data: dict = {}
    if request.content_type.startswith("application/json"):
        _data = request.get_data()
        return json.loads(_data.decode("utf-8"))
    if request.content_type.startswith("application/x-www-form-urlencoded"):
        # print(urllib.parse.parse_qs(request.get_data().decode("utf-8")))
        return parse_qs_plus(urllib.parse.parse_qs(request.get_data().decode("utf-8")))
    for key, value in request.form.items():
        if key.endswith("[]"):
            data[key[:-2]] = request.form.getlist(key)
        else:
            data[key] = value
    return data
