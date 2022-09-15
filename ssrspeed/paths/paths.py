import json
import os
import sys

_ = os.sep
WD_PATH = os.getcwd() + _
CURRENT_PATH = os.path.dirname(__file__) + _
JSON_PATH = f"{CURRENT_PATH}paths.json"
ROOT_PATH = _.join(CURRENT_PATH.split(_)[0:-2]) + _

INNER_PATH = {
    "ssrspeed": f"{ROOT_PATH}",
    "static": f"{ROOT_PATH}resource{_}static{_}",
    "fonts": f"{ROOT_PATH}resource{_}static{_}fonts{_}",
    "logos": f"{ROOT_PATH}resource{_}static{_}logos{_}",
    "templates": f"{ROOT_PATH}resource{_}templates{_}",
    "ssrspeed.example.json": f"{ROOT_PATH}resource{_}ssrspeed.example.json",
}


def get_path_json(work_path=WD_PATH):
    work_dir = work_path if work_path.endswith(_) else work_path + _
    inner_dict = {
        "data": f"{work_dir}data{_}",
        "logs": f"{work_dir}data{_}logs{_}",
        "results": f"{work_dir}data{_}results{_}",
        "tmp": f"{work_dir}data{_}tmp{_}",
        "uploads": f"{work_dir}data{_}tmp{_}uploads{_}",
        "config.json": f"{work_dir}data{_}tmp{_}config.json",
        "ssrspeed.json": f"{work_dir}data{_}ssrspeed.json",
        "resources": f"{work_dir}resources{_}",
        "clients": f"{work_dir}resources{_}clients{_}",
        "databases": f"{work_dir}resources{_}databases{_}",
        "custom": f"{work_dir}resources{_}custom{_}",
    }
    inner_dict.update(INNER_PATH)
    return inner_dict


def root():
    p = ROOT_PATH
    os.chdir(p)
    sys.path.insert(0, p)


if __name__ == "__main__":
    print(CURRENT_PATH)
    print(JSON_PATH)
    print(ROOT_PATH)
    print(WD_PATH)
    print(json.dumps(get_path_json(), indent=4))
