import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions

from config import urls


options = FirefoxOptions()
driver = webdriver.Firefox(options=options)
driver.set_window_size(1500, 1200)
driver.get(urls.url_briefing_domain)

# TODO comment
class BriefingParser:
    def __init__(self, url_string):
        self.target_url = urls.url_inPlay
        self.driver = driver
        self.html_text, self.soup = '', ''
        self.get_html_text()
        self.target_url = url_string
        self.get_html_text()
        self.get_soup()

    def set_new_url(self, new_url):
        self.target_url = new_url
        self.get_html_text()
        self.get_soup()

    def get_html_text(self):
        self.driver.get(self.target_url)
        time.sleep(15)
        self.html_text = self.driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")

    def get_soup(self):
        self.soup = BeautifulSoup(self.html_text, "html.parser")
