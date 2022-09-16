import os
from re import M
import selenium

from .base_parser import BaseParser
from .driver_builder import build_chrome_driver
from defines import DOWNLOAD_ROOT
from defines import WEBDRIVER_PATH
from defines import BINARY_LOCATION
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
    
    def __init__(self, driver=None):
        self._n_pages = 1
        self._page_url = "https://www.work.ua/resumes-it/?page={}".format

        self._driver = driver or build_chrome_driver()

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
        self._driver.get(url)

        resume_data = {
            "name": None,
            "position": None,
            "salary": None,
            "employment": None,
            "age": None,
            "city": None,
            "other_cities": None,
            "url": url
        }

        name = self._driver.find_element(
            By.CSS_SELECTOR,
            self._resume_page_items_path["name"]
        ).text
        resume_data["name"] = name
 
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

        resume_data["postion"] = position
        resume_data["salary"] = salary

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

        for pii_name, pii_value in zip(personal_information_item_names, personal_information_item_values):
            item_name = pii_name.text
            item_value = pii_value.text
            
            resume_data_key = values_keys[item_name.strip()]
            resume_data[resume_data_key] = item_value.strip()
            

        return resume_data

    def _get_resume_pages(self, url):
        self._driver.get(url)
        resume_cards = self._driver.find_elements(
            By.CSS_SELECTOR, 
            self._resumes_page_items_path["resume_cards"]
        )
        
        resume_urls = []

        for resume_card in resume_cards:
            title_ = resume_card.find_element(
                By.CSS_SELECTOR,
                self._resumes_page_items_path["resume_cards__title"]
            )

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

        for page_index in range(1, self._n_pages+1):
            url = self._page_url(page_index)
            resume_urls_ = self._get_resume_pages(url)
            resume_urls.extend(resume_urls_)
        
        for resume_url in resume_urls:
            resume_data = self._get_resume_data(resume_url)
            resumes_data.append(resume_data)
        
        return resumes_data




