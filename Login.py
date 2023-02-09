import rsa
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import base64
import qrcode
import Tools
import PIL
import requests
import json


class Login:
    def __init__(self, account=0, password=0):
        self.loginResp = None
        self.qrInfo = None
        self.seccode = None
        self.validate = None
        self.encodedPassword = None
        self.gt = None
        self.token = None
        self.challenge = None
        self.session = None
        self.password = password
        self.account = account

    def getCaptcha(self):
        captcha_url = "http://passport.bilibili.com/x/passport-login/captcha?source=main_web"
        captcha = requests.get(captcha_url)

        self.token = captcha.json().get("data").get("token")
        self.gt = captcha.json().get("data").get("geetest").get("gt")
        self.challenge = captcha.json().get("data").get("geetest").get("challenge")

    def captchaCertify(self):
        PATH = "./chromedriver"
        captcha_ctf = "https://kuresaru.github.io/geetest-validator/"

        driver = webdriver.Chrome(PATH)

        driver.get(captcha_ctf)
        driver.find_element(By.ID, "gt").send_keys(self.gt)
        driver.find_element(By.ID, "challenge").send_keys(self.challenge)
        driver.find_element(By.ID, "btn-gen").click()

        time.sleep(10)
        driver.find_element(By.ID, "btn-result")

        self.validate = driver.find_element(By.NAME, "geetest_validate").get_attribute("value")
        self.seccode = driver.find_element(By.NAME, "geetest_seccode").get_attribute("value")

    def encryptPassword(self):
        webKeyURL = "http://passport.bilibili.com/x/passport-login/web/key"

        web_key = requests.get(webKeyURL)
        RSAkey = web_key.json().get("data").get("key")
        salt = web_key.json().get("data").get("hash")

        pubKey = rsa.PublicKey.load_pkcs1_openssl_pem(RSAkey)
        encryptedPassword = rsa.encrypt((salt + self.password).encode(), pubKey)
        self.encodedPassword = base64.b64encode(encryptedPassword).decode()

    def login_by_password(self):
        loginURL = "http://passport.bilibili.com/x/passport-login/web/login"

        params = {
            "username": self.account,
            "password": self.encodedPassword,
            "keep": True,
            "token": self.token,
            "challenge": self.challenge,
            "validate": self.validate,
            "seccode": self.seccode
        }

        self.loginResp = requests.post(loginURL, data=params)

    def qr_generate(self, choice="web"):
        if choice == "tv":
            url = "https://passport.bilibili.com/x/passport-tv-login/qrcode/auth_code"

            data = {"appkey": "4409e2ce8ffd12b8",
                    "local_id": "0",
                    "ts": 0,
                    "sign": "e134154ed6add881d28fbdf68653cd9c"}

            self.qrInfo = requests.post(url, data=data).json()["data"]

        elif choice == "web":
            url = "http://passport.bilibili.com/x/passport-login/web/qrcode/generate"
            self.qrInfo = requests.get(url).json().get("data")

        qr = qrcode.QRCode(
            version=1,
            box_size=10,
            border=5)
        qr.add_data(self.qrInfo.get("url"))

        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        img.save('temp_img.png')

    def login_by_qr(self, choice="web"):
        # Login by tv is not working, tbf
        if choice == "tv":
            loginURL = "https://passport.bilibili.com/x/passport-tv-login/qrcode/poll"

            params = {"appkey": "4409e2ce8ffd12b8",
                      "auth_code": self.qrInfo["auth_code"],
                      "local_id": "0",
                      "ts": 0,
                      "sign": "e134154ed6add881d28fbdf68653cd9c"
                      }

            self.loginResp = requests.post(loginURL, params=params)

        elif choice == "web":
            loginURL = "http://passport.bilibili.com/x/passport-login/web/qrcode/poll"
            params = {"qrcode_key": self.qrInfo.get("qrcode_key")}
            self.loginResp = self.session.get(url=loginURL, params=params)

    def check_login(self):
        resp = self.session.get("https://api.bilibili.com/x/space/acc/info")
        if resp.json().get("code") == -101:
            print("Cookie outdated, requesting a new one")
            self.qr_generate()
            im = PIL.Image.open("temp_img.png", mode="r")
            im.show()
            im.close()
            time.sleep(10)
            self.login_by_qr()
            with open("sessdata.json", "w") as f:
                json.dump(self.session.cookies.get_dict(), f)
        else:
            print("Cookie valid")

    def load_cookie(self):
        try:
            with open("sessdata.json", "r") as f:
                cookies = json.load(f)
            self.session = requests.Session()
            self.session.cookies.update(cookies)
        except:
            self.session = requests.Session()
            self.check_login()
