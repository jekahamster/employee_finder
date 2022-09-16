import os
import time

from defines import DOWNLOAD_ROOT
from defines import WEBDRIVER_PATH
from defines import BINARY_LOCATION 
from selenium import webdriver
from selenium.webdriver import chrome
from selenium.webdriver import firefox
from selenium.webdriver.common.by import By


def _get_chrome_options(headless=True, tor=False, no_logging=False, detach=False):
        chrome_options = chrome.options.Options()
        
        if headless:
            chrome_options.add_argument("--headless")
        
        if no_logging:
            chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        if detach:
            chrome_options.add_experimental_option("detach", True)
        
        if tor:
            chrome_options.add_argument("--proxy-server=socks5://127.0.0.1:9150")
        
        # prefs = {
        #     "profile.default_content_setting_values.automatic_downloads": 1,
        #     "download.default_directory": str(DOWNLOAD_ROOT)   
        # }
        # chrome_options.binary_location = BINARY_LOCATION
        # chrome_options.add_experimental_option("prefs", prefs)
        return chrome_options


def build_chrome_driver(headless=False, tor=False, no_logging=False, detach=False):
    chrome_options = _get_chrome_options(headless=headless, tor=tor, no_logging=no_logging, detach=detach)
    service = chrome.service.Service(executable_path=str(WEBDRIVER_PATH))

    chrome_driver = webdriver.Chrome(service=service, options=chrome_options)
    return chrome_driver