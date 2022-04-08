import json
import os
import logging
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


def fill_login_form(drive_instance: webdriver):
    """Signs into a VK profile using environment variables.
    The instruction on how to create environment variables on Mac and Linux can be found in README.md"""
    phone_number = os.environ.get("PHONE_NUMBER")
    password = os.environ.get("PASSWORD")

    drive_instance.find_element(by=By.CLASS_NAME, value="FlatButton.FlatButton--primary.FlatButton--size-l.FlatButton--round.FlatButton--wide.UnauthActionBox__login.VkIdForm__button").click()
    # waits until the "Sign in" box shows up
    time.sleep(1.5)
    # inserts credentials stored in environment variables PHONE_NUMBER and PASSWORD
    drive_instance.find_element(by=By.NAME, value="login").send_keys(phone_number + Keys.ENTER)
    time.sleep(1.5)
    drive_instance.find_element(by=By.NAME, value="password").send_keys(password + Keys.ENTER)


def read_stored_cookies():
    with open("cookies.json", "r") as cookie_file:
        return json.load(cookie_file)


def add_all_cookies_to_session(drive_instance):
    for cookie in read_stored_cookies():
        try:
            drive_instance.add_cookie(cookie)
            logging.debug(f"Successfully added a cookie: {cookie}")
        except Exception as err:
            logging.error(f"Failed to add a cookie: {cookie}.\n Error message: {err}")