# coding:utf-8

import json
import logging
import os
import sys
import time

from flask import Flask, redirect, request  # ,render_template
from flask_cors import CORS
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

loggerList = []
loggerSub = logging.getLogger("Sub")
logger = logging.getLogger(__name__)
loggerList.append(loggerSub)
loggerList.append(logger)

formatter = logging.Formatter(
    "[%(asctime)s][%(levelname)s][%(thread)d][%(filename)s:%(lineno)d]%(message)s"
)
fileHandler = logging.FileHandler(
    LOGS_DIR + time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()) + ".log",
    encoding="utf-8",
)
fileHandler.setFormatter(formatter)
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(formatter)

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
                logger.info("Tmp config file saved as {}.".format(tmp_filename))
                return json.dumps(sc.web_read_config_file(tmp_filename))
            else:
                logger.error("Disallowed file {}.".format(ufile.filename))
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
                except:
                    pass
            for name in dirs:
                try:
                    os.remove(os.path.join(root, name))
                except:
                    pass
        sys.exit(0)

    if args.debug:
        DEBUG = args.debug
        for item in loggerList:
            item.setLevel(logging.DEBUG)
            item.addHandler(fileHandler)
            item.addHandler(consoleHandler)
    else:
        for item in loggerList:
            item.setLevel(logging.INFO)
            item.addHandler(fileHandler)
            item.addHandler(consoleHandler)

    logger.info(
        "SSRSpeed {}, Web Api Version {}".format(
            ssrconfig["VERSION"], ssrconfig["WEB_API_VERSION"]
        )
    )

    if logger.level == logging.DEBUG:
        logger.debug("Program running in debug mode.")

    if not args.skip_requirements_check:
        rc = RequirementsCheck()
        rc.check()
    else:
        logger.warning("Requirements check skipped.")

    sc = SSRSpeedCore()
    sc.web_mode = True
    if not os.path.exists(upload_dir):
        logger.warning("Upload folder {} not found, creating.".format(upload_dir))
        os.makedirs(upload_dir)
    app.run(host=args.listen, port=int(args.port), debug=DEBUG, threaded=True)
