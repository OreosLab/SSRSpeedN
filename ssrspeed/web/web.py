import json
import os

from flask import Flask, redirect, request  # ,render_template
from flask_cors import CORS
from loguru import logger
from werkzeug.utils import secure_filename

from ssrspeed.config import ssrconfig
from ssrspeed.core import SSRSpeedCore
from ssrspeed.type.errors.webapi import FileNotAllowed, WebFileCommonError
from ssrspeed.utils.web import get_post_data

ALLOWED_EXTENSIONS = {"json", "yml"}


def check_file_allowed(filename):
    return "." in filename and filename.rsplit(".", 1)[1] in ALLOWED_EXTENSIONS


def server_method(app, sc):
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
            # proxy_type = data.get("proxyType","SSR")
            if not subscription_url:
                return "invalid url."
            return json.dumps(sc.web_read_subscription(subscription_url))

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
        logger.warning(f"Upload folder {upload_dir} not found, creating.")
        os.makedirs(upload_dir)
    if args.port:
        port = args.port
    else:
        port = ssrconfig["web"]["port"]
    if args.listen:
        host = args.listen
    else:
        host = ssrconfig["web"]["listen"]
    app.run(host=host, port=port, debug=args.debug, threaded=True)
