import pathlib
import argparse


def build_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-c", "--cookies",
        action="store",
        default=None,
        type=pathlib.Path,
        dest="cookies_path",
        help="Path to saved cookies (default: None)"
    )

    parser.add_argument(
        "--search",
        default=None,
        type=str,
        dest="search_query",
        help="Query for searching on site"
    )

    parser.add_argument(
        "--sites",
        action="store",
        nargs="+",
        choices=["workua"],
        type=str,
        dest="sites",
        help="Sites where searching"
    )

    return parser