# coding:utf-8

import json
import os
import sys
import time

from flask import Flask, redirect, request  # ,render_template
from flask_cors import CORS
from loguru import logger
from werkzeug.utils import secure_filename

from ssrspeed.config import ssrconfig
from ssrspeed.core import SSRSpeedCore
from ssrspeed.paths import KEY_PATH
from ssrspeed.shell import web_cli as console_cfg
from ssrspeed.type.errors.webapi import FileNotAllowed, WebFileCommonError
from ssrspeed.utils import RequirementsCheck, check_platform
from ssrspeed.utils.web import get_post_data

WEB_API_VERSION = ssrconfig["WEB_API_VERSION"]

LOGS_DIR = KEY_PATH["logs"]
RESULTS_DIR = KEY_PATH["results"]

if not os.path.exists(LOGS_DIR):
    os.mkdir(LOGS_DIR)
if not os.path.exists(RESULTS_DIR):
    os.mkdir(RESULTS_DIR)

LOG_FILE = f"{LOGS_DIR}{time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())}.log"
logger_config = {
    "handlers": [
        {
            "sink": sys.stdout,
            "level": "INFO",
            "format": "[<green>{time:YYYY-MM-DD HH:mm:ss}</green>][<level>{level}</level>][<yellow>{file}</yellow>:<cyan>{line}</cyan>]: <level>{message}</level>",
            "colorize": True,  # 自定义配色
            "serialize": False,  # 以JSON数据格式打印
            "backtrace": True,  # 是否显示完整的异常堆栈跟踪
            "diagnose": True,  # 异常跟踪是否显示触发异常的方法或语句所使用的变量，生产环境因设为False
            "enqueue": True,  # 默认线程安全。若想实现协程安全 或 进程安全，该参数设为True
            "catch": True,  # 捕获异常
        },
        {
            "sink": LOG_FILE,
            "level": "INFO",
            "format": "[{time:YYYY-MM-DD HH:mm:ss}][{level}][{file}:{line}]: {message}",
            "serialize": False,
            "backtrace": True,
            "diagnose": True,
            "enqueue": True,
            "catch": True,
        },
    ]
}

template_dir = KEY_PATH["templates"]
static_dir = KEY_PATH["static"]
upload_dir = KEY_PATH["uploads"]
ALLOWED_EXTENSIONS = {"json", "yml"}

app = Flask(
    __name__,
    template_folder=template_dir,
    static_folder=static_dir,
    static_url_path="",
)

app.config["UPLOAD_FOLDER"] = upload_dir
CORS(app)
sc = None


@app.route("/", methods=["GET"])
def index():
    return redirect("https://web1.ospf.in/", 301)


# return render_template(
# 	"index.html"
# )

"""
{
    "proxyType": "SSR",      // [SSR, SSR-C#, SS, V2RAY]
    "testMethod": "SOCKET",  // [SOCKET, SPEED_TEST_NET, FAST]
    "testMode": "",          // [ALL, TCP_PING, WEB_PAGE_SIMULATION]
    "subscriptionUrl": "",
    "colors": "origin",
    "sortMethod": "",        // [SPEED, REVERSE_SPEED, PING, REVERSE_PING]
    "include": [],
    "includeGroup": [],
    "includeRemark": [],
    "exclude": [],
    "excludeGroup": [],
    "excludeRemark": []
}
"""


@app.route("/getversion", methods=["GET"])
def get_version():
    return json.dumps(
        {"main": ssrconfig["VERSION"], "webapi": ssrconfig["WEB_API_VERSION"]}
    )


@app.route("/status", methods=["GET"])
def status():
    return sc.web_get_status()


@app.route("/readsubscriptions", methods=["POST"])
def read_subscriptions():
    if request.method == "POST":
        data = get_post_data()
        if sc.web_get_status() == "running":
            return "running"
        subscription_url = data.get("url", "")
        # proxy_type = data.get("proxyType","SSR")
        if not subscription_url:
            return "invalid url."
        return json.dumps(sc.web_read_subscription(subscription_url))


def check_file_allowed(filename):
    return "." in filename and filename.rsplit(".", 1)[1] in ALLOWED_EXTENSIONS


@app.route("/readfileconfig", methods=["POST"])
def read_file_config():
    if request.method == "POST":
        if sc.web_get_status() == "running":
            return "running"
        ufile = request.files["file"]
        # data = get_post_data()
        if ufile:
            if check_file_allowed(ufile.filename):
                filename = secure_filename(ufile.filename)
                tmp_filename = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                ufile.save(tmp_filename)
                logger.info(f"Tmp config file saved as {tmp_filename}.")
                return json.dumps(sc.web_read_config_file(tmp_filename))
            else:
                logger.error(f"Disallowed file {ufile.filename}.")
                return FileNotAllowed.errMsg
        else:
            logger.error("File upload failed or unknown error.")
            return WebFileCommonError.errMsg


@app.route("/getcolors", methods=["GET"])
def get_colors():
    return json.dumps(sc.web_get_colors())


@app.route("/start", methods=["POST"])
def start_test():
    if request.method == "POST":
        data = get_post_data()
        # 	return "SUCCESS"
        if sc.web_get_status() == "running":
            return "running"
        configs = data.get("configs", [])
        if not configs:
            return "No configs"
        # proxy_type = data.get("proxyType","SSR")
        test_method = data.get("testMethod", "ST_ASYNC")
        colors = data.get("colors", "origin")
        sort_method = data.get("sortMethod", "")
        test_mode = data.get("testMode", "")
        use_ssr_cs = data.get("useSsrCSharp", False)
        group = data.get("group", "")
        sc.web_setup(
            testMode=test_mode,
            testMethod=test_method,
            colors=colors,
            sortMethod=sort_method,
        )
        sc.clean_result()
        sc.web_set_configs(configs)
        if group:
            sc.set_group(group)
        sc.start_test(use_ssr_cs)
        return "done"
    return "invalid method"


@app.route("/getresults")
def get_results():
    return json.dumps(sc.web_get_results())


if __name__ == "__main__":
    pfInfo = check_platform()
    if pfInfo == "Unknown":
        logger.critical(
            "Your system does not support it. Please contact the developer."
        )
        sys.exit(1)

    DEBUG = False

    args = console_cfg.init(WEB_API_VERSION)

    if args.paolu:
        for root, dirs, files in os.walk("..", topdown=False):
            for name in files:
                try:
                    os.remove(os.path.join(root, name))
                except Exception:
                    pass
            for name in dirs:
                try:
                    os.remove(os.path.join(root, name))
                except Exception:
                    pass
        sys.exit(0)

    if args.debug:
        DEBUG = args.debug
        for each in logger_config["handlers"]:
            each.update({"level": "DEBUG"})
        logger.debug("Program running in debug mode.")
        logger.configure(**logger_config)
    else:
        logger.configure(**logger_config)
    logger.enable("__main__")

    logger.info(
        f'SSRSpeed {ssrconfig["VERSION"]}, Web Api Version {ssrconfig["WEB_API_VERSION"]}'
    )

    if not args.skip_requirements_check:
        rc = RequirementsCheck()
        rc.check()
    else:
        logger.warning("Requirements check skipped.")

    sc = SSRSpeedCore()
    sc.web_mode = True
    if not os.path.exists(upload_dir):
        logger.warning(f"Upload folder {upload_dir} not found, creating.")
        os.makedirs(upload_dir)
    app.run(host=args.listen, port=int(args.port), debug=DEBUG, threaded=True)
