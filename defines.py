import os 
import pathlib

ROOT_DIR = pathlib.Path(os.path.dirname(os.path.abspath(__file__)))
DRIVERS_ROOT = ROOT_DIR / "webdrivers"
DOWNLOAD_ROOT = ROOT_DIR / "downloads"

# Chrome
WEBDRIVER_PATH = DRIVERS_ROOT / "chromedriver.exe"
BINARY_LOCATION = "C:\\Program Files\\Google\\Chrome Beta\\Application\\chrome.exe"

# # Tor
# WEBDRIVER_PATH = DRIVERS_ROOT / "geckodriver.exe"
# BINARY_LOCATION = "D:\\Tor Browser\\Browser\\firefox.exe"