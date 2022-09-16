import json
import os
import sys
import time

from loguru import logger

from ssrspeed import __version__ as version, __banner__ as banner
from ssrspeed.download import download
from ssrspeed.paths import JSON_PATH, get_path_json
from ssrspeed.shell import cli as cli_cfg
from ssrspeed.config import ssrconfig, generate_config_file, load_path_config
from ssrspeed.utils import PLATFORM, RequirementsCheck


def init_dir(paths):
    for path in paths:
        if not os.path.exists(path):
            os.makedirs(path)


def check_dir(paths):
    flag = False  # 检测必要文件夹是否存在
    for path in paths:
        if not os.path.exists(path):
            os.makedirs(path)
            flag = True  # 发送文件夹建立行为
    if flag:
        logger.warning("Please download the resource and store it in the specified location!")
        exit(0)


def generate_path_json(data, file):
    with open(file=file, mode="w", encoding="utf-8") as f:
        f.write(json.dumps(data, indent=4))


def get_handlers(logs_dir):
    log_file = f"{logs_dir}{time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())}.log"
    return [
        {
            "sink": sys.stdout,
            "level": "INFO",
            "format": "[<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green>][<level>{level}</level>]"
            "[<yellow>{file}</yellow>:<cyan>{line}</cyan>]: <level>{message}</level>",
            "colorize": True,  # 自定义配色
            "serialize": False,  # 以 JSON 数据格式打印
            "backtrace": True,  # 是否显示完整的异常堆栈跟踪
            "diagnose": True,  # 异常跟踪是否显示触发异常的方法或语句所使用的变量，生产环境应设为 False
            "enqueue": True,  # 默认线程安全。若想实现协程安全 或 进程安全，该参数设为 True
            "catch": True,  # 捕获异常
        },
        {
            "sink": log_file,
            "level": "INFO",
            "format": "[{time:YYYY-MM-DD HH:mm:ss.SSS}][{level}][{file}:{line}]: {message}",
            "serialize": False,
            "backtrace": True,
            "diagnose": True,
            "enqueue": True,
            "catch": True,
        },
    ]


def main():
    if PLATFORM == "Unknown":
        logger.critical("Your system is not supported. Please contact the developer.")
        sys.exit(1)
    else:
        os.system("clear" if PLATFORM != "Windows" else "cls")
        print(banner)
    args = cli_cfg.init(version)

    # 生成项目路径字典
    if args.dir:
        key_path = get_path_json(work_path=args.dir)
    else:
        key_path = get_path_json()

    if download_type := args.download:
        download(download_type, PLATFORM, args.dir)

    # 生成项目路径 json 文件
    generate_path_json(key_path, JSON_PATH)
    # 导入路径JSON数据拷贝至缓存
    load_path_config(key_path)
    # 生成配置文件并将配置文件JSON数据拷贝至缓存
    generate_config_file()
    # 配置日志格式及日志文件路径
    handlers = get_handlers(key_path["logs"])
    # 检测外部资源目录(不存在，则建议资源文件夹，供用户存放运行依赖资源)
    check_dir([key_path["clients"], key_path["databases"]])
    # 初始化临时文件、日志和结果集目录(非项目依赖项)
    init_dir(
        [key_path["tmp"], key_path["logs"], key_path["custom"], key_path["results"]]
    )
    if ssrconfig['fastSpeed'] is True:
        for each in handlers:
            each.update({"enqueue": False})
    # 部署日志模板
    if args.debug:
        for each in handlers:
            each.update({"level": "DEBUG"})
        logger.debug("Program running in debug mode.")
        logger.configure(handlers=handlers)
    else:
        logger.configure(handlers=handlers)
    logger.enable("__main__")

    logger.info(f"SSRSpeed {version}")

    if not args.skip_requirements_check:
        rc = RequirementsCheck(key_path["clients"], key_path["databases"])
        rc.check()
    else:
        logger.warning("Requirements check skipped.")

    if args.web:
        
        from ssrspeed.web import start_server
        
        start_server(args, key_path)
        
    else:
        config_url = ""
        config_filename = ""

        if args.url:
            config_load_mode = 0
            config_url = args.url
        elif args.import_file:
            config_load_mode = 1
        elif args.guiConfig:
            config_load_mode = 2
            config_filename = args.guiConfig
        else:
            logger.error("No config input, exiting...")
            sys.exit(1)

        test_mode_dict = {
            "default": "DEFAULT",
            "pingonly": "TCP_PING",
            "stream": "STREAM",
            "all": "ALL",
            "wps": "WEB_PAGE_SIMULATION",
        }
        test_mode = test_mode_dict.get(args.test_mode, "DEFAULT")

        test_method_dict = {
            "stasync": "ST_ASYNC",
            "socket": "SOCKET",
            "speedtestnet": "SPEED_TEST_NET",
            "fast": "FAST",
        }
        test_method = test_method_dict.get(args.test_method, "ST_ASYNC")

        filter_keyword = args.filter
        filter_group_keyword = args.group
        filter_remark_keyword = args.remarks
        exclude_keyword = args.efilter
        exclude_group_keyword = args.egfilter
        exclude_remark_keyword = args.erfilter

        result_image_color = args.result_color

        sort_method_dict = {
            "speed": "SPEED",
            "rspeed": "REVERSE_SPEED",
            "ping": "PING",
            "rping": "REVERSE_PING",
        }
        sort_method = sort_method_dict.get(args.sort_method, "")

        logger.debug(
            f"Test mode: {test_mode}"
            f"\nTest method: {test_method}"
            f"\nFilter keyword : {filter_keyword}"
            f"\nFilter group : {filter_group_keyword}"
            f"\nFilter remark : {filter_remark_keyword}"
            f"\nExclude keyword : {exclude_keyword}"
            f"\nExclude group : {exclude_group_keyword}"
            f"\nExclude remark : {exclude_remark_keyword}"
            f"\nSort method : {sort_method}"
        )

        # SSRSpeedCore 方法需配置文件支持，故在此导入
        from ssrspeed.core import SSRSpeedCore

        sc = SSRSpeedCore()

        if args.url and config_load_mode == 0:
            sc.console_setup(
                test_mode, test_method, result_image_color, sort_method, url=config_url
            )
        elif args.import_file and config_load_mode == 1:
            import_filename = args.import_file
            sc.colors = result_image_color
            sc.sort_method = sort_method if sort_method else ""
            sc.import_and_export(import_filename)
            sys.exit(0)
        else:
            sc.console_setup(
                test_mode,
                test_method,
                result_image_color,
                sort_method,
                cfg_filename=config_filename,
            )

        if args.group_override:
            sc.set_group(args.group_override)

        sc.filter_nodes(
            fk=filter_keyword,
            fgk=filter_group_keyword,
            frk=filter_remark_keyword,
            ek=exclude_keyword,
            egk=exclude_group_keyword,
            erk=exclude_remark_keyword,
        )

        sc.clean_result()

        sc.start_test(args)


if __name__ == "__main__":
    main()
