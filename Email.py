import smtplib

class Send_Email:
    def __init__(self,email,user,item):
        self.user="morninggood4345@gmail.com"
        self.password="elsalfwlzwtyxbyn"
        self.email=email
        self.u=user
        self.item=item


    def low_price(self):
        with open("Low_price message.txt",mode="r") as file:
            message=file.read()
        message=message.replace("[Product]",f"{self.item.name}[f{self.item.url_name}]")
        message=message.replace("[Price]",f"{self.item.low_price}")
        with smtplib.SMTP("smtp.gmail.com",port=587) as connection:
            connection.starttls()
            connection.login(user=self.user,password=self.password)
            connection.sendmail(from_addr=self.user,to_addrs=self.email,msg=message)


    def budget(self):
        with open(file="budget message.txt",mode="r") as file:
            message=file.read()
        message=message.replace("[Product]", f"{self.item.name}[f{self.item.url_name}]")
        message=message.replace("[Price]", f"{self.item.price}")
        with smtplib.SMTP("smtp.gmail.com",port=587) as connection:
            connection.starttls()
            connection.login(user=self.user,password=self.password)
            connection.sendmail(from_addr=self.user,to_addrs=self.email,msg=message)
