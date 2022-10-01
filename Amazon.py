import bs4
from bs4 import BeautifulSoup
import requests
import lxml
from Email import Send_Email

class Amazon_Price:
    def __init__(self,url):
        self.url=url
        self.headers = {
                "Request Line": "GET / HTTP/1.1",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "en-US,en;q=0.9",
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"
            }

    def get_add(self):
        self.response = requests.get(url=self.url, headers=self.headers)
        self.webpage = self.response.text
        self.soup = BeautifulSoup(self.webpage, "html.parser")
        self.price_tag = self.soup.find(name="span", class_="a-offscreen")
        self.price = self.price_tag.get_text()
        self.price=self.price.split("₹")[1]
        self.price=self.price.replace(",","")
        self.price = float(self.price)
        self.price=int(self.price)
        self.title_tag = self.soup.find(name="span", id="productTitle")
        self.name = self.title_tag.getText()
        img_tag=self.soup.find(name="img",id="landingImage")
        self.img_url=img_tag["src"]

    def get_price(self):
        self.response = requests.get(url=self.url, headers=self.headers)
        self.webpage = self.response.text
        self.soup = BeautifulSoup(self.webpage, "html.parser")
        self.price_tag = self.soup.find(name="span", class_="a-offscreen")
        self.price = self.price_tag.get_text()
        self.price = self.price.split("₹")[1]
        self.price = self.price.replace(",", "")
        self.price = float(self.price)
        self.price = int(self.price)

    def update(self,users,db):
        for user in users:
            for item in user.items:
                self.response = requests.get(url=item.url, headers=self.headers)
                self.webpage = self.response.text
                self.soup = BeautifulSoup(self.webpage, "html.parser")
                self.price_tag = self.soup.find(name="span", class_="a-offscreen")
                self.price = self.price_tag.get_text()
                self.price = self.price.split("₹")[1]
                self.price = self.price.replace(",", "")
                self.price = float(self.price)
                self.price = int(self.price)
                item.price=self.price
                db.session.commit()
                if self.price < int(item.low_price):
                    item.low_price = self.price
                    db.session.commit()
                    email = Send_Email(email=user.email, user=user, item=item)
                    email.low_price()
                if self.price < int(item.budget):
                    email = Send_Email(email=user.email, user=user, item=item)
                    email.budget()
