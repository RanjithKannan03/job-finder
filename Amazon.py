import bs4
from bs4 import BeautifulSoup
import requests
import lxml
from Email import Send_Email
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from Email import Send_Email
import os

# class Amazon_Price:
#     def __init__(self,url):
#         self.url=url
#         self.headers = {
#                 "Request Line": "GET / HTTP/1.1",
#                 "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
#                 "Accept-Encoding": "gzip, deflate",
#                 "Accept-Language": "en-US,en;q=0.9",
#                 "Connection": "keep-alive",
#                 "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"
#             }
#         self.http_proxy = "http://10.10.1.10:3128"
#         self.https_proxy = "https://10.10.1.11:1080"
#         self.ftp_proxy = "ftp://10.10.1.10:3128"
#
#         self.proxyDict = {
#             "http": self.http_proxy,
#             "https": self.https_proxy,
#             "ftp": self.ftp_proxy
#         }
#
#     def get_add(self):
#         self.response = requests.get(url=self.url, headers=self.headers)
#         self.webpage = self.response.text
#         self.soup = BeautifulSoup(self.webpage, "html.parser")
#         self.price_tag = self.soup.find(name="span", class_="a-offscreen")
#         self.price = self.price_tag.get_text()
#         self.price=self.price.split("₹")[1]
#         self.price=self.price.replace(",","")
#         self.price = float(self.price)
#         self.price=int(self.price)
#         self.title_tag = self.soup.find(name="span", id="productTitle")
#         self.name = self.title_tag.getText()
#         img_tag=self.soup.find(name="img",id="landingImage")
#         self.img_url=img_tag["src"]
#
#     def get_price(self):
#         self.response = requests.get(url=self.url, headers=self.headers)
#         self.webpage = self.response.text
#         self.soup = BeautifulSoup(self.webpage, "html.parser")
#         self.price_tag = self.soup.find(name="span", class_="a-offscreen")
#         self.price = self.price_tag.get_text()
#         self.price = self.price.split("₹")[1]
#         self.price = self.price.replace(",", "")
#         self.price = float(self.price)
#         self.price = int(self.price)
#
#     def update(self,users,db):
#         for user in users:
#             for item in user.items:
#                 self.response = requests.get(url=item.url, headers=self.headers)
#                 self.webpage = self.response.text
#                 self.soup = BeautifulSoup(self.webpage, "html.parser")
#                 self.price_tag = self.soup.find(name="span", class_="a-offscreen")
#                 self.price = self.price_tag.get_text()
#                 self.price = self.price.split("₹")[1]
#                 self.price = self.price.replace(",", "")
#                 self.price = float(self.price)
#                 self.price = int(self.price)
#                 item.price=self.price
#                 db.session.commit()
#                 if self.price < int(item.low_price):
#                     item.low_price = self.price
#                     db.session.commit()
#                     email = Send_Email(email=user.email, user=user, item=item)
#                     email.low_price()
#                 if self.price < int(item.budget):
#                     email = Send_Email(email=user.email, user=user, item=item)
#                     email.budget()

class Amazon_Price:
    def __init__(self,url):
        self.url=url
        chrome_options=webdriver.ChromeOptions()
        chrome_options.binary_location=os.environ.get("GOOGLE_CHROME_BIN")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        chrome_driver_path = os.environ.get("CHROMEDRIVER_PATH")
        # ser = Service(chrome_driver_path)
        # op = webdriver.ChromeOptions()
        # op.add_argument('headless')
        self.driver = webdriver.Chrome(executable_path=chrome_driver_path,chrome_options=chrome_options)

    def get_add(self):
        self.driver.get(url=self.url)
        name_tag=self.driver.find_element(By.ID,"productTitle")
        self.name=name_tag.text
        img_tag=self.driver.find_element(By.CSS_SELECTOR,".imgTagWrapper img")
        self.img_url=img_tag.get_attribute("src")
        price_tag=self.driver.find_element(By.CLASS_NAME,"a-price-whole")
        self.price=price_tag.text
        self.price = price_tag.text.replace(",", "")
        self.driver.close()

    def get_price(self):
        self.driver.get(url=self.url)
        price_tag = self.driver.find_element(By.CLASS_NAME, "a-price-whole")
        self.price = price_tag.text.replace(",","")
        self.driver.close()
