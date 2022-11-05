import sqlite3

from defines import DB_PATH


def _create_if_not_exist(curr):
    query = """
        CREATE TABLE IF NOT EXISTS `user_data` (
            `id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
            `first_name` VARCHAR(255),
            `last_name` VARCHAR(255),
            `middle_name` VARCHAR(255),
            `position` VARCHAR(255),
            `email` VARCHAR(255),
            `phone` VARCHAR(15),
            `date` DATETIME DEFAULT CURRENT_TIMESTAMP,
            `origin` VARCHAR(255),
            `url` VARCHAR(255) UNIQUE
        );
    """
    curr.execute(query)


def dict_factory(cursor, row):
    d = {}
    for idx,col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class Storage:
    def __init__(self, db_path=DB_PATH):
        self._db = sqlite3.connect(db_path)
        self._db.row_factory = dict_factory
        self._curr = self._db.cursor()
        _create_if_not_exist(self._curr)
    
    def __del__(self):
        self._db.commit()
        self._db.close()

    def insert(self,
        first_name=None,
        last_name=None,
        middle_name=None,
        email=None,
        phone=None,
        date=None,
        origin=None,
        url=None):
        
        query = """
            INSERT INTO `user_data` (first_name, last_name, middle_name, email, phone, date, origin, url)
            VALUES (:first_name, :last_name, :middle_name, :email, :phone, :date, :origin, :url);
        """
        
        query_params = {
            "first_name": first_name,
            "last_name": last_name,
            "middle_name": middle_name,
            "email": email,
            "phone": phone,
            "date": date,
            "origin": origin,
            "url": url
        }
        
        self._curr.execute(query, query_params)
        self._db.commit()

    def find_by_url(self, url):
        query = """
            SELECT *
            FROM `user_data`
            WHERE url = :url
        """
        params = {"url": url}

        query_results = self._curr.execute(query, params)
        return query_results.fetchone()
