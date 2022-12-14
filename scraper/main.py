import os
import sys
import pathlib
import argparse

from defines import DB_PATH
from .parsers import WorkUaParser
from .parsers import RabotaUaParser
from argument_parser_builder import build_argument_parser
from driver_builder import build_chrome_driver


def _check_ip(driver):
    import requests
    import re

    from selenium.webdriver.common.by import By
    
    ip_pattern = re.compile(r"[\d]{1,3}\.[\d]{1,3}\.[\d]{1,3}\.[\d]{1,3}")
    url = "http://icanhazip.com/"

    response = requests.request(method="GET", url=url)
    global_ip = ip_pattern.findall(response.text)[0]

    driver.get(url)
    driver_ip = driver.find_element(By.CSS_SELECTOR, "pre").text

    assert driver_ip != global_ip, "Tor is not activated"
    return driver_ip


def main(args):
    arg_parser = build_argument_parser()
    arguments = arg_parser.parse_args(args)

    db_path = arguments.db_path or DB_PATH
    n_pages = arguments.n_pages
    tor = arguments.tor
    detach = arguments.detach
    no_logging = arguments.no_logging
    headless = arguments.headless

    driver = build_chrome_driver(
        headless=headless, 
        detach=detach, 
        no_logging=no_logging, 
        tor=tor
    )
    
    if tor:
        ip = _check_ip(driver)
        print("IP:", ip)


if __name__ == "__main__":
    main(sys.argv[1:])
