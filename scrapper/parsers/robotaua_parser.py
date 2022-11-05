import re
import requests
import time
import json
import warnings
import sqlite3

from tqdm import tqdm
from datetime import datetime
from defines import DB_PATH
from driver_builder import build_chrome_driver
from .base_parser import BaseParser
from .storage import Storage
from selenium.webdriver.common.by import By
from seleniumrequests import Chrome
from selenium.webdriver.support.ui import WebDriverWait




class RobotaUaParser(BaseParser):
    _login_items_path = {
        "email_input": "#ctl00_content_ZoneLogin_txLogin",
        "pass_input": "#ctl00_content_ZoneLogin_txPassword",
        "login_button": "#ctl00_content_ZoneLogin_btnLogin" 
    }

    _resumes_page_items_path = {
        "employer-list-card-a": "alliance-employer-cvdb-cv-list-card alliance-shared-link-wrapping a",
    }

    _resume_page_items_path = {
        "left_side": "alliance-cv-detail-page alliance-employer-cvdb-resume alliance-employer-cvdb-desktop-resume-content > div > div:nth-child(1)",
        "right_side": "alliance-cv-detail-page alliance-employer-cvdb-resume alliance-employer-cvdb-desktop-resume-content > div .main-info-wrapper lib-resume-main-info .resume-main-wrapper",
    }

    _resume_id_pattern = re.compile(r"[\d]+")

    def __init__(self, driver=None, db_path=DB_PATH, n_pages=100):
        self._driver = driver or build_chrome_driver(headless=True, tor=False, no_logging=False, detach=False)
        self._db_path = db_path
        self._n_pages = n_pages
        self._storage = Storage(db_path=db_path)
        self._login_page = "https://rabota.ua/ua/employer/login"
        self._main_page = "https://rabota.ua/"
        self._pages_url_pattern = "https://rabota.ua/ua/candidates/all/%D0%B2%D1%81%D1%8F_%D1%83%D0%BA%D1%80%D0%B0%D0%B8%D0%BD%D0%B0?pg={}&rubrics=%5B%221%22%5D".format

    def login(self, login, password):
        self._driver.get(self._login_page)
        email_input = self._driver.find_element(
            By.CSS_SELECTOR, 
            self._login_items_path["email_input"])
        pass_input = self._driver.find_element(
            By.CSS_SELECTOR, 
            self._login_items_path["pass_input"])
        loggin_button = self._driver.find_element(
            By.CSS_SELECTOR, 
            self._login_items_path["login_button"])

        email_input.send_keys(login)
        pass_input.send_keys(password)
        loggin_button.click()

    def login_by_cookies(self, cookies):
        self._driver.get(self._main_page)
        self.set_cookies(cookies)

    def set_cookies(self, cookies:dict):
        for cookie in cookies:
            self._driver.add_cookie(cookie)

    def get_cookies(self):
        return self._driver.get_cookies()
    
    def _wait_resumes_page_loading(self, timeout=300):
        wait = WebDriverWait(self._driver, timeout=timeout)
        wait.until(
            lambda driver: len(driver.find_elements(By.CSS_SELECTOR, self._resumes_page_items_path) > 0)
        )

    def _get_resume_pages(self, url):
        self._driver.get(url)
        time.sleep(10)

        employer_cards_a = self._driver.find_elements(
            By.CSS_SELECTOR,
            self._resumes_page_items_path["employer-list-card-a"]
        )

        assert len(employer_cards_a) > 0, "No cards on page"

        resume_urls = []
        for employer_card_a in employer_cards_a:
            resume_url = employer_card_a.get_attribute("href")
            resume_urls.append(resume_url)

        return resume_urls
        
    def _get_resume_data(self, url):
        user_by_url = self._storage.find_by_url(url)
        if user_by_url:
            return user_by_url

        resume_id = self._resume_id_pattern.search(url).group()
        resume_request_url = f"https://employer-api.rabota.ua/resume/{resume_id}"

        resume_data_response = requests.request("GET", resume_request_url)
        resume_data_response_json = json.loads(resume_data_response.text)

        spetiality = resume_data_response_json.get("speciality", "")
        seo_tags = resume_data_response_json.get("seoTags", [])
        first_name = resume_data_response_json.get("name", "")
        last_name = resume_data_response_json.get("surname", "")
        middle_name = resume_data_response_json.get("fatherName", "")
        str_date = resume_data_response_json.get("addDate", None)
        email = resume_data_response_json.get("email", "")
        phone = resume_data_response_json.get("phone", "")

        if str_date:
            str_date = str_date[:str_date.find(".")]
            date = datetime.fromisoformat("2022-11-03T13:33:29")
        else:
            date = None

        for seo_tag in seo_tags:
            pz_name = seo_tag.get("pzName", "")
            spetiality += f", {pz_name}"
        
        user_data = {
            "first_name": first_name,
            "last_name": last_name,
            "middle_name": middle_name,
            "position": spetiality,
            "email": email,
            "phone": phone,
            "date": date,
            "origin": "rabota.ua",
            "url": url
        }

        return user_data


    def get_data(self):
        resume_urls = []
        resumes_data = []

        for page_index in tqdm(range(1, self._n_pages)):
            url = self._pages_url_pattern(page_index)
            resume_urls_from_page = self._get_resume_pages(url) 
            resume_urls.extend(resume_urls_from_page)
        
        for resume_url in tqdm(resume_urls):
            try:
                resume_data = self._get_resume_data(resume_url)
                resumes_data.append(resume_data)
            except Exception as e:
                print(f"Exception at {resume_url}")
                print(e)
                continue

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
