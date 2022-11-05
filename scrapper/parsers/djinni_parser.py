from calendar import month
import requests
import socks 
import socket
import re
import warnings
import sqlite3

from datetime import datetime
from tqdm import tqdm
from defines import DB_PATH
from bs4 import BeautifulSoup
from .base_parser import BaseParser
from driver_builder import build_chrome_driver
from selenium.webdriver.common.by import By
from .storage import Storage


class DjinniParser(BaseParser):
    _login_items_path = {
        "email_input": "#email",
        "password_input": "#password",
        "submit_button": ".btn.btn-primary.btn-lg"
    }

    _resumes_items_path = {
        "resume_titles_a": ".searchresults .list__title .profile"
    }

    _resume_items_path = {
        "position": ".page-header h1",
        "date": ".candidate-right div p",
    }

    def __init__(self, driver=None, db_path=DB_PATH, n_pages=100, tor=False):
        self._driver = driver or build_chrome_driver(headless=True, tor=False, no_logging=False, detach=False)
        self._db_path = db_path
        self._storage = Storage(db_path=db_path)
        self._n_pages = n_pages
        self._page_url_pattern = "https://djinni.co/developers/?page={}".format

    def login(self, email, password):
        url = "https://djinni.co/login?from=frontpage_main"
        self._driver.get(url)
        
        email_input = self._driver.find_element(By.CSS_SELECTOR, self._login_items_path["email_input"])
        password_input = self._driver.find_element(By.CSS_SELECTOR, self._login_items_path["password_input"])
        submit_button = self._driver.find_element(By.CSS_SELECTOR, self._login_items_path["submit_button"])

        email_input.send_keys(email)
        password_input.send_keys(password)
        submit_button.click()

    def login_by_cookies(self, cookies):
        self._driver.get(self._main_page)
        self.set_cookies(cookies)

    def set_cookies(self, cookies:dict):
        for cookie in cookies:
            self._driver.add_cookie(cookie)

    def get_cookies(self):
        return self._driver.get_cookies()

    def _get_resume_pages(self, url):
        response = requests.request(
            method="GET", 
            url=url
        )
        document = BeautifulSoup(markup=response.text, features="html.parser")
        resume_titles_a = document.select(self._resumes_items_path["resume_titles_a"])

        resumes_urls = []

        for resume_title_a in resume_titles_a:
            title = resume_title_a.text.strip()
            link = f"https://djinni.co{resume_title_a.get('href')}"

            resumes_urls.append(link)
        
        return resumes_urls
    
    def _get_cookies_for_headers(self):
        cookies = self._driver.get_cookies()

        if not cookies:
            raise "You had to login using login(email, password) or load cookies"

        str_cookies = []

        for cookie in cookies:
            str_cookies.append(f"{cookie['name']}={cookie['value']}")

        return ";".join(str_cookies)

    def _get_headers(self):

        str_cookies = self._get_cookies_for_headers()

        headers={
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "ru-RU,ru-UA;q=0.9,ru;q=0.8,uk-UA;q=0.7,uk;q=0.6,en-US;q=0.5,en;q=0.4",
            # "cookie": "_ga=GA1.2.1154604291.1666907952; intercom-id-cg6zpunb=6f689bc5-36d4-4893-ba5d-37cda24f32b8; _gid=GA1.2.2025918804.1667248287; csrftoken=TG6kpYNkJ5z8TgyuTnnVg0Lpl7mGMdgGlT1Oeob7PyQHbTKai6Ma24GXtqi1hoZv; _gat=1; sessionid=.eJxVj7tOw0AQRf9lW4g1O_vekhbRIKitmX3ECZEt-VGgyP_OGqWAds6952ruoqdtHfptKXN_ySIKi0prK57_Aqb0VcaD5iuN56lL07jOF-6OSPegS_c25XJ7eWT_CQZahtYOijM5V6snbSxIGzzXarRUkpzRDBxQuSSpeOer45Sd0swYZKZAAZo0TVub_u5T22rGz9f3dqRxGkW8i98HAKFKYKgGi3ZOs0OV2XqDWVW28pDMhdZyhBEQTxJOSn4gRIXR2C6glyE8AUQ4FuuNzkuz7_v-A1dAWu8:1opsgR:dxaUrDq5KLaGLB3cL-ViULC3fhBVwFwRoWuHUGgmRKg; intercom-session-cg6zpunb=WFFZRGtwOEZpb0d1TVROZWJWRkNkSWtHSDBQeDBETHJFb3RDck1ZKzRpbXptWksvL0hDbHBEL2hvWkVyMkVqYy0tZ3FtSzhHUDRIMzNpL1B5NlJkRzJwQT09--3f6646390fdb8e9f6e0e03c8627462e54b6fded6",
            "cookie": str_cookies,
            "sec-ch-ua": '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": 'document',
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36"
        }
        return headers

    def _get_resume_date(self, document):
        date_ = document.select_one(self._resume_items_path["date"])
        
        if not date_:
            # return datetime.now()
            return None
        
        date_is = date_.find_all("i")
        date_spans = date_.find_all("span")

        for elem in [*date_is, *date_spans]:
            if elem:
                elem.decompose()
        
        date_str = date_.text.replace("Опубліковано", "").strip().lower()
        re_searching_res = re.search(r"([\d]{1,2}) ([а-яіїєґ]+) ([\d]{4})", date_str)

        if not re_searching_res:
            return None

        str_day, str_month, str_year = re_searching_res.group(1, 2, 3)
        ua_months_to_number = {
            "січня":    1,
            "лютого":   2,
            "березня":  3,
            "квітня":   4,
            "травня":   5,
            "червня":   6,
            "липня":    7,
            "серпня":   8,
            "вересня":  9,
            "жовтня":   10,
            "листопада": 11,
            "грудня":   12
        }

        day = int(str_day)
        month = ua_months_to_number[str_month]
        year = int(str_year)
        date = datetime(year, month, day)
        return date

    def _get_resume_data(self, url):
        user_by_url = self._storage.find_by_url(url)
        if user_by_url:
            return user_by_url
        
        response = requests.request(method="GET", url=url, headers=self._get_headers())
        document = BeautifulSoup(response.text, "html.parser")

        position = document.select_one(self._resume_items_path["position"]).text.strip()
        date = self._get_resume_date(document)

        resume_data = {
            "first_name": "",
            "last_name": "",
            "middle_name": "",
            "position": position,
            "email": "",
            "phone": "",
            "date": date,
            "origin": "djinni.co",
            "url": url
        }

        return resume_data


    def get_data(self):
        if not self._driver.get_cookies():
            raise "You have to login using login(email, passwod) or load cookis"

        pages_links = []
        resumes_data = []

        for page_index in tqdm(range(1, self._n_pages+1)):
            resume_pages = self._get_resume_pages(self._page_url_pattern(page_index))
            pages_links.extend(resume_pages)

        for resume_page_url in tqdm(pages_links):
            try:
                resume_data = self._get_resume_data(resume_page_url)
                resumes_data.append(resume_data)
            except Exception as e:
                print(e)
                print(f"URL: {resume_page_url}")

        for resume_data in resumes_data:
            try:
                self._storage.insert(
                    first_name=resume_data["first_name"],
                    last_name=resume_data["last_name"],
                    middle_name=resume_data["middle_name"],
                    position=resume_data["position"],
                    email=resume_data["email"],
                    phone=resume_data["phone"],
                    origin=resume_data["origin"],
                    url=resume_data["url"]
                )
            except sqlite3.IntegrityError:
                warnings.warn(f"Person {resume_data['url']} in database")

        return resumes_data
        
