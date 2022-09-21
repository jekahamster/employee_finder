import pathlib
import argparse

from defines import DB_PATH


def build_argument_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-d", "--dbpath",
        action="store",
        default=DB_PATH,
        type=pathlib.Path,
        dest="db_path",
        help="Path to db"
    )

    parser.add_argument(
        "-n", "--npages",
        action="store",
        default=100,
        type=int,
        dest="n_pages",
        help="Count of visited pages"
    )

    parser.add_argument(
        "--tor",
        action="store_true",
        dest="tor",
        help="Run scrapper in tor network (Tor browser mus be runned)"
    )

    parser.add_argument(
        "--detach",
        action="store_true",
        dest="detach",
        help="Detach browser after parsing is finished"
    )

    parser.add_argument(
        "--no-logging",
        action="store_true",
        dest="no_logging",
        help="Do not show log information"
    )

    parser.add_argument(
        "--headless",
        action="store_true",
        dest="headless",
        help="Dont show browser gui",
    )

    # parsers_group = parser.add_argument_group()
    
    # parsers_group.add_argument(
    #     "--all",
    #     action="store_true",
    #     dest="all",
    #     help="Use all sites"
    # )

    # parsers_group.add_argument(
    #     "--workua",
    #     action="store_true",
    #     dest="workua",
    #     help="Use work.ua"
    # )

    return parser