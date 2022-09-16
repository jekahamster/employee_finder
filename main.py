import os 
import sys
import pathlib
import argparse
import pickle
import json

from parsers import WorkUaParser
from parser_builder import build_parser
from parsers.driver_builder import build_chrome_driver


def load_cookies(path):
    cookies = None
    
    with open(path, "rb") as file:
        cookies = pickle.load(file)
    
    assert cookies is not None, "Empty cookies"
    return cookies


def save_cookies(cookies, path):
    with open(path, "wb") as file:
        pickle.dump(cookies, file)


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
    driver = build_chrome_driver(detach=False, no_logging=False, tor=True)
    ip = _check_ip(driver)
    print("IP:", ip)

    parser = WorkUaParser(driver=driver)
    resumes_data = parser.get_data()

    for resume_data in resumes_data:
        print(resume_data)

if __name__ == "__main__":
    main(sys.argv[1:])
