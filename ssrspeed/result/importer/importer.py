import json


def import_result(filename):
    with open(filename, "r", encoding="utf-8") as f:
        fi = json.loads(f.read())
    return fi
