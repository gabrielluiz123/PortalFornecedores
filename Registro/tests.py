from django.test import TestCase
import os
BASE_DIR = \
    os.path.dirname(os.path.abspath(__file__))
os.environ["PATH"] += os.path.join(BASE_DIR,'../gecko')


from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys



class AuthTestCase(LiveServerTestCase):
    def test_login(self):

        driver = webdriver.Chrome()
        driver.get('http://127.0.0.1:8000/')

        entrar = driver.find_element_by_id('btnLogin')
        entrar.click()

        user = driver.find_element_by_name('email')
        pwd = driver.find_element_by_name('pwd')

        submit = driver.find_element_by_id('btnAuth')

        user.send_keys('admin')
        pwd.send_keys('admin')
        submit.send_keys(Keys.RETURN)