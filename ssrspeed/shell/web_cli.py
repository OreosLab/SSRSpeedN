import logging
from argparse import ArgumentParser, Namespace

from ssrspeed.config import ssrconfig

logger = logging.getLogger("Sub")


def set_opts(parser: ArgumentParser):
    parser.add_argument(
        "-l",
        "--listen",
        action="store",
        dest="listen",
        default=ssrconfig["web"]["listen"],
        help="Set listen address for web server.",
    )
    parser.add_argument(
        "-p",
        "--port",
        action="store",
        dest="port",
        default=ssrconfig["web"]["port"],
        help="Set listen port for web server.",
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
    args = parser.parse_args()
    return args
