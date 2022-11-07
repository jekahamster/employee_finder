import os
import traceback
import random
import time

from datetime import datetime
from tqdm import tqdm
from defines import SEO_TAGS_CACHE
from driver_builder import build_chrome_driver
from .base_parser import BaseParser
from storage import Storage
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


class _LinkedInAccount:
    _resume_page_items_path = {
        "name": "h1.text-heading-xlarge",
        "short_info": 'section.artdeco-card:has(div[id="profile-sticky-header-toggle"]) div.text-body-medium',
        "experience_card": 'section.artdeco-card:has(div[id="experience"])',
        "experience_card__list_items": "ul.pvs-list.ph5 > li",
        "experience_card__list_items__name": 'span.mr1.t-bold span[aria-hidden="true"]',
        # if span.pvs-entity__path-node exists in experience_card__list_items, then user have 
        # many positions (like Python Developer, Technical Leed) inside one company.
        # In this case (if span.pvs-entity__path-node exists), experience_card__list_items__name
        # contains company name, not position name, so we need check names from inner positions
        "experience_card__list_items__inner_positions": "ul.pvs-list > li:has(> span.pvs-entity__path-node)", 
        "experience_card__list_items__inner_positions__name": 'div.pvs-entity a.optional-action-target-wrapper span.mr1 span[aria-hidden="true"]'
    }

    def __init__(self, url, driver):
        self._url = url
        self._driver = driver or build_chrome_driver(headless=True, tor=False, no_logging=False, detach=False)
        
        self._name = None
        self._first_name = None 
        self._last_name = None
        self._short_info = None
        self._experience = []

        self.scrape()

    def _get_inner_positions_names(self, experience_item):
        names = []
        
        inner_positions = experience_item.find_elements(
            By.CSS_SELECTOR,
            self._resume_page_items_path
        )

        for inner_position in inner_positions:
            name = inner_position.find_element(
                By.CSS_SELECTOR,
                self._resume_page_items_path["experience_card__list_items__inner_positions__name"]
            )
            names.append(name)
        
        return names

    def get_experience(self):
        experience_names = set()

        experience_card = self._driver.find_element(
            By.CSS_SELECTOR,
            self._resume_page_items_path["experience_card"]
        )

        experience_items = experience_card.find_elements(
            By.CSS_SELECTOR,
            self._resume_page_items_path["experience_card__list_items"]
        )

        for experience_item in experience_items:
            experience_item_names = experience_item.find_elements(
                By.CSS_SELECTOR,
                self._resume_page_items_path["experience_card__list_items__name"]
            )

            if len(experience_item_names) > 1:
                experience_names_ = [
                    experience_item_name.get_attribute("innerText").strip()
                    for experience_item_name in experience_item_names[1:]
                ]
                experience_names.update(experience_names_)
            else:
                experience_name = experience_item_names[0].get_attribute("innerText").strip()
                experience_names.add(experience_name)

        return list(experience_names)

    def scrape(self):
        self._driver.get(self._url)
        time.sleep(5)

        # name
        self._name = self._driver.find_element(
            By.CSS_SELECTOR,
            self._resume_page_items_path["name"]
        ).text.strip()
        
        self._first_name, self._last_name = self._name.split()

        # short info under the name
        self._short_info = self._driver.find_element(
            By.CSS_SELECTOR,
            self._resume_page_items_path["short_info"]
        ).text.strip()

        # work experience
        try:
            self._experience = self.get_experience()
        except:
            pass

    def __str__(self):
        result = f"LinkedInAccount(name='{self._name}', " + \
            f"first_name='{self._first_name}', " + \
            f"last_name='{self._last_name}', " + \
            f"short_info='{self._short_info}', " + \
            f"experience={self._experience}"
        return result

    @property
    def name(self):
        return self._name

    @property
    def first_name(self):
        return self._first_name

    @property
    def last_name(self):
        return self._last_name

    @property
    def short_info(self):
        return self._short_info

    @property
    def experience(self):
        return self._experience



class LinkedInParser(BaseParser):
    _login_items_path = {
        "email_or_phone_input": "#username",
        "password_input": "#password",
        "sign_in_button": "form .login__form_action_container button"
    }

    _resume_pages_items_path = {
        "resume_a": "ul.reusable-search__entity-result-list > li.reusable-search__result-container div.entity-result__content a.app-aware-link"   
    }


    def __init__(self, driver=None, db_path=None, n_pages=100, seo_tags_count=5):
        self._driver = driver or build_chrome_driver(headless=True, tor=False, no_logging=False, detach=False)
        self._db_path = db_path
        self._storage = Storage(db_path=db_path)
        self._count_of_pages = None
        self._n_pages = n_pages
        self._seo_tags_count = seo_tags_count

    def login(self, login, password):
        url = "https://www.linkedin.com/login?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin"
        self._driver.get(url)

        email_or_phone_input = self._driver.find_element(
            By.CSS_SELECTOR,
            self._login_items_path["email_or_phone_input"]
        )

        password_input = self._driver.find_element(
            By.CSS_SELECTOR,
            self._login_items_path["password_input"]
        )

        sign_in_button = self._driver.find_element(
            By.CSS_SELECTOR,
            self._login_items_path["sign_in_button"]
        )

        email_or_phone_input.send_keys(login)
        password_input.send_keys(password)
        sign_in_button.click()
        time.sleep(1)
        if self._driver.current_url.startswith("https://www.linkedin.com/checkpoint/challenge"):
            print("Enter captcha")
            os.system("pause")
            
    def _get_url(self, query, page=None):
        formated_query = query.strip().replace(" ", "%20")
        url = f"https://www.linkedin.com/search/results/people/?keywords={formated_query}&origin=GLOBAL_SEARCH_HEADER"
        
        if page:
            url += f"&page={page}"
        
        return url

    def get_resume_pages(self, url):
        self._driver.get(url)

        resume_cards_a = self._driver.find_elements(
            By.CSS_SELECTOR,
            self._resume_pages_items_path["resume_a"]
        )

        resume_urls = []
        for resume_card_a in resume_cards_a:
            resume_url = resume_card_a.get_attribute("href")
            # print(resume_url)
            
            resume_urls.append(resume_url)

        return resume_urls

    def _get_seo_tags(self, n=5, seo_tags_path=SEO_TAGS_CACHE):
        with open(seo_tags_path, "r", encoding="UTF-8") as seo_tags_file:
            seo_tags = seo_tags_file.readlines()
        seo_tags = list(map(lambda x: x.strip(), seo_tags))
        random.shuffle(seo_tags)
        return seo_tags[:n]

    def get_resume_data(self, url):
        user_by_url = self._storage.find_by_url(url)
        if user_by_url:
            return user_by_url

        account = _LinkedInAccount(url=url, driver=self._driver)

        resume_data = {
            "first_name": account.first_name,
            "last_name": account.last_name,
            "middle_name": "",
            "position": ", ".join(account.experience),
            "email": "",
            "phone": "",
            "date": datetime.today(),
            "origin": "linkedin",
            "url": url
        }

        return resume_data

    def get_data(self, search_queries=None):
        resume_urls = []
        resumes_data = [] 

        queries = []
        if search_queries and isinstance(search_queries, str):
            queries.append(search_queries)
        
        elif search_queries and isinstance(search_queries, (list, tuple)):
            queries.extend(search_queries)

        seo_tags = self._get_seo_tags(n=self._seo_tags_count)
        queries.extend(seo_tags)

        for index, query in enumerate(queries):
            print(f"Query {index+1}/{len(queries)}")
            print(f"Query: {query}")

            for page_index in tqdm(range(1, self._n_pages+1)):
                url = self._get_url(query, page=page_index)
                resume_urls_from_page = self.get_resume_pages(url)
                resume_urls.extend(resume_urls_from_page)
        
        for resume_url in tqdm(resume_urls):
            try:
                resume_data = self.get_resume_data(resume_url)
                resumes_data.append(resume_data)
            except:
                print(traceback.format_exc())
                print(f"URL: {resume_url}")

        return resumes_data
