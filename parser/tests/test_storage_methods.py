import sys 
sys.path.append("..")

import pathlib
import unittest
import os

from defines import ROOT_DIR
from parsers.storage import Storage
from parsers.driver_builder import build_chrome_driver


class TestStorageMethods(unittest.TestCase):
    def setUp(self):
        self.db_path = ROOT_DIR / "tests" / "test.db"
        self.storage = Storage(db_path=self.db_path)
        return super().setUp()

    def clear_db(self):
        self.storage._curr.execute("""
            DELETE FROM `user_data`;
        """)
        self.storage._db.commit()

    def tearDown(self):
        del self.storage
        os.remove(self.db_path)
        return super().tearDown()

    # def test_insert_count(self):
    #     self.storage.insert(
    #         first_name="FirstName",
    #         last_name="LastName",
    #         middle_name="MiddleName",
    #         email="test@mail.mail",
    #     )
    #     query = """
    #         SELECT * 
    #         FROM `user_data`;
    #     """
    #     res = self.storage._curr.execute(query).fetchall()
        
    #     expected_output = [
    #         {
    #             'id': 1, 
    #             'first_name': 'FirstName', 
    #             'last_name': 'LastName', 
    #             'middle_name': 'MiddleName', 
    #             'position': None, 
    #             'email': 'test@mail.mail', 
    #             'phone': None, 
    #             'date': None, 
    #             'origin': None, 
    #             'url': None
    #         }
    #     ]

    #     self.clear_db

    #     self.assertEqual(res, expected_output)

    
    def test_find_by_url(self):
        self.clear_db()

        url = "url1"
        self.storage.insert(
            first_name = '1', 
            last_name = '11', 
            middle_name = '111', 
            email = 'test@mail.mail', 
            phone = None, 
            date = None, 
            origin = None, 
            url = "url1"
        )
        self.storage.insert(
            first_name = '2', 
            last_name = '22', 
            middle_name = '222', 
            email = 'test@mail.mail', 
            phone = None, 
            date = None, 
            origin = None, 
            url = "url1"
        )
        
        
        res = self.storage.find_by_url(url)

        print("res:")
        print(res)

        self.clear_db()

    