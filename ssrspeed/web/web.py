import json
import os

from flask import Flask, redirect, request  # ,render_template
from flask_cors import CORS
from loguru import logger
from werkzeug.utils import secure_filename

from ssrspeed.config import ssrconfig
from ssrspeed.core import SSRSpeedCore
from ssrspeed.type.error.webapi import FileNotAllowed, WebFileCommonError
from ssrspeed.util.web import get_post_data

ALLOWED_EXTENSIONS = {"json", "yml"}


def check_file_allowed(filename):
    return "." in filename and filename.rsplit(".", 1)[1] in ALLOWED_EXTENSIONS


def server_method(app, sc):
    @app.route("/", methods=["GET"])
    def index():
        return redirect("https://web1.ospf.in/", 301)

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
        return json.dumps({"main": ssrconfig["VERSION"]})

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
            return (
                json.dumps(sc.web_read_subscription(subscription_url))
                if subscription_url
                else "invalid url."
            )

        return "invalid method"

    @app.route("/readfileconfig", methods=["POST"])
    def read_file_config():
        if request.method != "POST":
            return "invalid method"

        if sc.web_get_status() == "running":
            return "running"
        ufile = request.files["file"]
        if ufile:
            if check_file_allowed(ufile.filename):
                filename = secure_filename(ufile.filename)
                tmp_filename = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                ufile.save(tmp_filename)
                logger.info(f"Tmp config file saved as {tmp_filename}.")
                return json.dumps(sc.web_read_config_file(tmp_filename))
            logger.error(f"Disallowed file {ufile.filename}.")
            return FileNotAllowed.err_msg
        logger.error("File upload failed or unknown error.")
        return WebFileCommonError.err_msg

    @app.route("/getcolors", methods=["GET"])
    def get_colors():
        return json.dumps(sc.web_get_colors())

    @app.route("/start", methods=["POST"])
    def start_test():
        if request.method != "POST":
            return "invalid method"

        data = get_post_data()
        if sc.web_get_status() == "running":
            return "running"
        configs = data.get("configs", [])
        if not configs:
            return "No configs"
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

    @app.route("/getresults")
    def get_results():
        return json.dumps(sc.web_get_results())


def start_server(args, key_path):
    template_dir = key_path["templates"]
    static_dir = key_path["static"]
    upload_dir = key_path["uploads"]

    app = Flask(
        __name__,
        template_folder=template_dir,
        static_folder=static_dir,
        static_url_path="",
    )
    app.config["UPLOAD_FOLDER"] = upload_dir
    CORS(app)
    sc = SSRSpeedCore()
    server_method(app, sc)
    sc.web_mode = True
    if not os.path.exists(upload_dir):
        logger.warning(f" Upload folder {upload_dir} not found, creating.")
        os.makedirs(upload_dir)
    port = args.port or ssrconfig["web"]["port"]
    host = args.listen or ssrconfig["web"]["listen"]
    app.run(host=host, port=port, debug=args.debug, threaded=True)
