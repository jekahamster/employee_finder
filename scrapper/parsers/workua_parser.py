import os
import selenium
import sqlite3
import warnings
import storage

from datetime import datetime
from .base_parser import BaseParser
from driver_builder import build_chrome_driver
from tqdm import tqdm
from defines import DOWNLOAD_ROOT
from defines import WEBDRIVER_PATH
from defines import BINARY_LOCATION
from defines import DB_PATH
from selenium import webdriver
from selenium.webdriver import chrome 
from selenium.webdriver.common.by import By


class WorkUaParser(BaseParser):
    # _login_items_paths = {}
    _resumes_page_items_path = {
        "resume_cards": "#pjax-resume-list > .card.card-hover.resume-link.wordwrap",
        "resume_cards__title": "h2",
        "resume_cards__url": "h2 > a",
    }
    _resume_page_items_path = {
        "name": 'div[id^="resume_"] .row h1',
        "position_salary": 'div[id^="resume_"] .row h2',
        "personal_information_item_names": 'div[id^="resume_"] .row .dl-horizontal dt',
        "personal_information_item_values": 'div[id^="resume_"] .row .dl-horizontal dd',
    }
    
    def __init__(self, driver=None, db_path=DB_PATH, n_pages=100):
        self._n_pages = n_pages
        self._page_url = "https://www.work.ua/resumes-it/?page={}".format

        self._driver = driver or build_chrome_driver()
        self._storage = storage.Storage(db_path)

    def sign_in(self, cookies):
        url = "https://www.work.ua/"
        self.driver.get(url)
        
        for cookie in cookies:
            self.driver.add_cookie(cookie)

    def user_control(self, url=None):
        if url:
            self.driver.get(url)
        
        os.system("pause")

    def _get_resume_data(self, url):
        user_by_url = self._storage.find_by_url(url)
        if user_by_url:
            return user_by_url
            
        self._driver.get(url)

        name = self._driver.find_element(
            By.CSS_SELECTOR,
            self._resume_page_items_path["name"]
        ).text
 
        position_salary = self._driver.find_element(
            By.CSS_SELECTOR,
            self._resume_page_items_path["position_salary"]
        )
        
        position = None
        salary = None
        try:
            salary = position_salary.find_element(By.CSS_SELECTOR, "span").text.replace(",", "").strip()
            position = ",".join(position_salary.text.split(",")[:-1])
        except selenium.common.exceptions.NoSuchElementException:
            position = position_salary.text

        personal_information_item_names = self._driver.find_elements(
            By.CSS_SELECTOR,
            self._resume_page_items_path["personal_information_item_names"]
        )
        personal_information_item_values = self._driver.find_elements(
            By.CSS_SELECTOR,
            self._resume_page_items_path["personal_information_item_values"]
        )
        values_keys = {
            "Зайнятість:": "employment",
            "Вік:": "age",
            "Місто:": "city",
            "Місто проживання:": "city",
            "Готовий працювати:": "other_cities"
        }

        personal_information = {}
        for pii_name, pii_value in zip(personal_information_item_names, personal_information_item_values):
            item_name = pii_name.text
            item_value = pii_value.text
            
            resume_data_key = values_keys[item_name.strip()]
            personal_information[resume_data_key] = item_value.strip()

        resume_data = {
            "first_name": name,
            "last_name": "",
            "middle_name": "",
            "position": position,
            "email": "",
            "phone": "",
            "date": datetime.today(),
            "origin": "work.ua",
            "url": url
        }
        
        return resume_data

    def _get_resume_pages(self, url):
        self._driver.get(url)
        resume_cards = self._driver.find_elements(
            By.CSS_SELECTOR, 
            self._resumes_page_items_path["resume_cards"]
        )
        
        resume_urls = []

        for resume_card in resume_cards:
            # title_ = resume_card.find_element(
            #     By.CSS_SELECTOR,
            #     self._resumes_page_items_path["resume_cards__title"]
            # )
            # resume_title = title_.text

            resume_url = resume_card.find_element(
                By.CSS_SELECTOR,
                self._resumes_page_items_path["resume_cards__url"]
            ).get_attribute("href")

            resume_urls.append(resume_url)
        
        return resume_urls

    def get_data(self):
        resume_urls = []
        resumes_data = []

        print("Collecting pages")
        for page_index in tqdm(range(1, self._n_pages+1)):
            url = self._page_url(page_index)
            resume_urls_ = self._get_resume_pages(url)
            resume_urls.extend(resume_urls_)
        
        print("Collecting resumes")
        for resume_url in tqdm(resume_urls):
            resume_data = self._get_resume_data(resume_url)
            resumes_data.append(resume_data)

        return resumes_data




