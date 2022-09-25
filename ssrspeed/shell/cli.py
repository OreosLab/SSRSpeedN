import sys
from argparse import ArgumentParser, Namespace


def set_opts(parser: ArgumentParser):
    parser.add_argument(
        "-d",
        "--dir",
        action="store",
        dest="dir",
        type=str,
        help="Specify a work directory with clients and data.",
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
        "-i",
        "--import",
        action="store",
        dest="import_file",
        default="",
        help="Import test result from json file and export it.",
    )
    parser.add_argument(
        "-c",
        "--config",
        action="store",
        dest="guiConfig",
        default="",
        help="Load configurations from file.",
    )
    parser.add_argument(
        "-mc",
        "--max-connections",
        action="store",
        dest="max_connections",
        type=int,
        help="Set max number of connections.",
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
        "-m",
        "--method",
        action="store",
        dest="test_method",
        default="",
        choices=["stasync", "socket", "speedtestnet", "fast"],
        help="Select test method in [stasync, socket, speedtestnet, fast].",
    )
    parser.add_argument(
        "--reject-same",
        action="store_true",
        dest="reject_same",
        default=False,
        help="Reject nodes that appear later with the same server and port as before.",
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
        "--include-group",
        action="extend",
        nargs="+",
        dest="group",
        default=[],
        help="Filter nodes by group name using keyword.",
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
        "--exclude",
        action="extend",
        nargs="+",
        dest="efilter",
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
        "-g",
        action="store",
        dest="group_override",
        default="",
        help="Manually set group.",
    )
    parser.add_argument(
        "-C",
        "--color",
        action="store",
        dest="result_color",
        default="origin",
        help="Set the colors when exporting images..",
    )
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
        "--skip-requirements-check",
        action="store_true",
        dest="skip_requirements_check",
        default=False,
        help="Skip requirements check.",
    )
    parser.add_argument(
        "-w", "--web", action="store_true", dest="web", help="Start web server."
    )
    parser.add_argument(
        "-l",
        "--listen",
        action="store",
        dest="listen",
        help="Set listen address for web server.",
    )
    parser.add_argument(
        "-p",
        "--port",
        action="store",
        dest="port",
        type=int,
        help="Set listen port for web server.",
    )
    parser.add_argument(
        "--download",
        action="store",
        dest="download",
        choices=["all", "client", "database"],
        help="Download resources in ['all', 'client', 'database']",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        dest="debug",
        default=False,
        help="Run program in debug mode.",
    )


def init(version: str) -> Namespace:
    parser = ArgumentParser(prog="ssrspeed")
    parser.add_argument("--version", action="version", version=version)
    set_opts(parser)
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)
    return parser.parse_args()
