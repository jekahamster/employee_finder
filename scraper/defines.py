import os 
import pathlib

ROOT_DIR = pathlib.Path(os.path.dirname(os.path.abspath(__file__)))
COOKIES_DIR = ROOT_DIR / "cookies"
SEO_TAGS_CACHE = ROOT_DIR / "cache" / "seo_tags.txt"
DRIVERS_ROOT = ROOT_DIR / "webdrivers"
DOWNLOAD_ROOT = ROOT_DIR / "downloads"
DB_PATH = ROOT_DIR / ".." / "employee_finder_web" / "db.sqlite3"
TABLE_NAME = "employee_finder_api_employees"

# Chrome
WEBDRIVER_PATH = DRIVERS_ROOT / "chromedriver_106.exe"
BINARY_LOCATION = "C:\\Program Files\\Google\\Chrome Beta\\Application\\chrome.exe"

# # Tor
# WEBDRIVER_PATH = DRIVERS_ROOT / "geckodriver.exe"
# BINARY_LOCATION = "D:\\Tor Browser\\Browser\\firefox.exe"