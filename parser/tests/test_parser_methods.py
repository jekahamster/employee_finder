import sys 
sys.path.append("..")

import pathlib
import unittest

from defines import ROOT_DIR
from parsers import WorkUaParser
from parsers.driver_builder import build_chrome_driver


class TestParserMethods(unittest.TestCase):
    DB_PATH = ROOT_DIR / "tests" / "test.db"
    
    def test_get_resume_data(self):
        driver = build_chrome_driver(headless=True, detach=False, tor=False, no_logging=False)
        parser = WorkUaParser(driver=driver, db_path=self.DB_PATH)

        url = "https://www.work.ua/resumes/6523203/"
        resume_data = parser._get_resume_data(url)
        
        expected_output = {
            "name": "Микола",
            "position": "Junior Project Manager",
            "salary": None,
            "employment": "Повна зайнятість.",
            "age": "29 років",
            "city": "Київ",
            "other_cities": None,
            "url": url
        }

        self.assertEqual(expected_output, resume_data)
        

if __name__ == "__main__":
    unittest.main()