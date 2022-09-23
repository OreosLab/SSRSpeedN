import json
import os
import shutil
import time

from loguru import logger


class ExporterWps:
    def __init__(self, result: list, results_dir: str, templates_dir: str):
        now_time = []
        for item in result:
            item["geoIP"]["inbound"]["address"] = "*.*.*.*"
            item["geoIP"]["outbound"]["address"] = "*.*.*.*"
            now_time.append(item)
        self.__results: list = now_time
        self.__results_dir: str = results_dir
        self._templates_dir: str = templates_dir

    def export(self):
        now_time = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
        fileloc = self.__results_dir + now_time
        res = "var res = " + json.dumps(
            self.__results, sort_keys=True, indent=4, separators=(",", ":")
        )
        if os.path.exists(fileloc):
            shutil.rmtree(fileloc)
        shutil.copytree(self._templates_dir, fileloc)
        filename = os.path.join(fileloc, "results.js")
        with open(filename, "w+", encoding="utf-8") as f:
            f.writelines(res)
        index_filename = os.path.join(fileloc, "index.html")
        with open(index_filename, "r", encoding="utf-8") as f:
            read = f.readlines()
        index = "".join(read)
        index = index.replace(r"{{ $generatedTime }}", now_time)
        with open(index_filename, "w+", encoding="utf-8") as f:
            f.writelines(index)
        logger.info(f"Web page simulation result exported as {fileloc}")


if __name__ == "__main__":
    from ssrspeed.path import ROOT_PATH, get_path_json

    key_path = get_path_json(ROOT_PATH)
    er = ExporterWps([], key_path["results"], key_path["templates"])
    er.export()
