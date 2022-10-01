from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from Email import Send_Email

class Amazon_Price:
    def __init__(self,url):
        self.url=url
        chrome_driver_path = "C:\Development\chromedriver.exe"
        ser = Service(chrome_driver_path)
        op = webdriver.ChromeOptions()
        op.add_argument('headless')
        self.driver = webdriver.Chrome(service=ser, options=op)

    def get_add(self):
        self.driver.get(url=self.url)
        name_tag=self.driver.find_element(By.ID,"productTitle")
        self.name=name_tag.text
        img_tag=self.driver.find_element(By.CSS_SELECTOR,".imgTagWrapper img")
        self.img_url=img_tag.get_attribute("src")
        price_tag=self.driver.find_element(By.CLASS_NAME,"a-price-whole")
        self.price=price_tag.text
        self.price = price_tag.text.replace(",", "")
        self.price = int(self.price)
        self.driver.close()

    def get_price(self):
        self.driver.get(url=self.url)
        price_tag = self.driver.find_element(By.CLASS_NAME, "a-price-whole")
        self.price = price_tag.text.replace(",","")
        self.price=int(self.price)
        self.driver.close()

    def update(self,users,db):
        for user in users:
            for item in user.items:
                self.driver.get(url=item.url)
                price_tag = self.driver.find_element(By.CLASS_NAME, "a-price-whole")
                self.price = price_tag.text.replace(",", "")
                self.price = int(self.price)
                self.driver.close()
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
