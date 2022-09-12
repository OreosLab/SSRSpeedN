import sys
from argparse import ArgumentParser, Namespace


def set_opts(parser: ArgumentParser):
    parser.add_argument(
        "-c",
        "--config",
        action="store",
        dest="guiConfig",
        default="",
        help="Load configurations from file.",
    )
    parser.add_argument(
        "-u",
        "--url",
        action="store",
        dest="url",
        default="",
        help="Load ssr config from subscription url.",
    )
    parser.add_argument(
        "-m",
        "--method",
        action="store",
        dest="test_method",
        default="stasync",
        choices=["speedtestnet", "fast", "socket", "stasync"],
        help="Select test method in [speedtestnet, fast, socket, stasync].",
    )
    parser.add_argument(
        "-M",
        "--mode",
        action="store",
        dest="test_mode",
        default="default",
        choices=["default", "pingonly", "stream", "all", "wps"],
        help="Select test mode in [default, pingonly, stream, all, wps].",
    )
    parser.add_argument(
        "--include",
        action="extend",
        nargs="+",
        dest="filter",
        default=[],
        help="Filter nodes by group and remarks using keyword.",
    )
    parser.add_argument(
        "--include-remark",
        action="extend",
        nargs="+",
        dest="remarks",
        default=[],
        help="Filter nodes by remarks using keyword.",
    )
    parser.add_argument(
        "--include-group",
        action="extend",
        nargs="+",
        dest="group",
        default=[],
        help="Filter nodes by group name using keyword.",
    )
    parser.add_argument(
        "--exclude",
        action="extend",
        nargs="+",
        dest="efliter",
        default=[],
        help="Exclude nodes by group and remarks using keyword.",
    )
    parser.add_argument(
        "--exclude-group",
        action="extend",
        nargs="+",
        dest="egfilter",
        default=[],
        help="Exclude nodes by group using keyword.",
    )
    parser.add_argument(
        "--exclude-remark",
        action="extend",
        nargs="+",
        dest="erfilter",
        default=[],
        help="Exclude nodes by remarks using keyword.",
    )
    parser.add_argument(
        "--use-ssr-cs",
        action="store_true",
        dest="use_ssr_cs",
        default=False,
        help="Replace the ShadowsocksR-libev with the ShadowsocksR-C# (Only Windows).",
    )
    parser.add_argument(
        "-g",
        action="store",
        dest="group_override",
        default="",
        help="Manually set group.",
    )
    """
    parser.add_argument(
        "-t","--type",
        action="store",
        dest="proxy_type",
        type=str,
        default = "ssr",
        help="Select proxy type in [ssr, ssr-cs, ss, v2ray], default ssr."
        )
    """
    parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        dest="confirmation",
        default=False,
        help="Skip node list confirmation before test.",
    )
    parser.add_argument(
        "-C",
        "--color",
        action="store",
        dest="result_color",
        default="",
        help="Set the colors when exporting images..",
    )
    """
    parser.add_argument(
        "-s","--split",
        action="store",
        dest="split_count",
        default="-1",
        help="Set the number of nodes displayed in a single image when exporting images."
    """
    parser.add_argument(
        "-s",
        "--sort",
        action="store",
        dest="sort_method",
        default="",
        choices=["speed", "rspeed", "ping", "rping"],
        help="Select sort method in [speed, rspeed, ping, rping], default not sorted.",
    )
    parser.add_argument(
        "-i",
        "--import",
        action="store",
        dest="import_file",
        default="",
        help="Import test result from json file and export it.",
    )
    parser.add_argument(
        "-mc",
        "--max-connections",
        action="store",
        dest="max_connections",
        type=int,
        help="Max number of connections",
    )
    parser.add_argument(
        "--skip-requirements-check",
        action="store_true",
        dest="skip_requirements_check",
        default=False,
        help="Skip requirements check.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        dest="debug",
        default=False,
        help="Run program in debug mode.",
    )
    parser.add_argument(
        "--paolu", action="store_true", dest="paolu", default=False, help="rm -rf *"
    )


def init(version: str) -> Namespace:
    parser = ArgumentParser(prog="ssrspeed")
    parser.add_argument("--version", action="version", version=version)
    set_opts(parser)
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)
    args = parser.parse_args()
    return args
