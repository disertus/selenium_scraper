import datetime
import json
import logging
import os
import time
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as ec


logging.basicConfig(filename="Logs.log",
                    format='%(asctime)s %(message)s',
                    level=logging.WARNING)

def scroll_once(wait_time: float):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(wait_time)


def write_to_file(dict_to_write, filename):
    with open(f"{project_path}/{filename}.txt", "a+") as file:
        json.dump(dict_to_write, file)
        file.write("\n")


def fill_login_form():
    driver.find_element(by=By.CLASS_NAME, value="JoinForm__signIn").click()
    driver.find_element(by=By.NAME, value="email").send_keys("PHONE_NUMBER")
    driver.find_element(by=By.NAME, value="pass").send_keys("PASSWORD" + Keys.ENTER)


def unfold_all_comments(post, id):
    try:
        temp_set = set()
        comments_list = post.find_elements(by=By.CLASS_NAME, value="js-replies_next_label")
        [temp_set.add(item.text) for item in comments_list]
        if "Show more comments" in temp_set:
            for com in comments_list:
                if com.text == "Show more comments":
                    com.click()
                    time.sleep(2)
                else:
                    continue
            unfold_all_comments(post, id)
        else:
            parse_comment_contents(post, id)
    except Exception as e:
        logging.warning(f"Did not find any comments to unfold. Error: {e}")
        try:
            parse_comment_contents(post, id)
        except Exception as e:
            logging.warning(f"Failed to parse any content from current post. Error: {e}")


def parse_post_contents():
    posts = driver.find_elements(by=By.CLASS_NAME, value="post_content")
    for post in posts:
        try:
            time.sleep(1)
            post_id = post.find_element(by=By.CLASS_NAME, value="wall_post_cont._wall_post_cont").get_attribute("id")
        except Exception as e:
            logging.warning(f"Failed to identify post ID. Error: {e}")
            post_id = ""
        if post_id not in post_ids:
            post_ids.add(post_id)
            yield post
        else:
            logging.debug(f"Post {post_id} has already been scanned. Proceeding to the next one.\n")
            scroll_once(3)
            parse_post_contents()


def count_likes(reply_content):
    try:
        return reply_content.find_element(by=By.CLASS_NAME, value="like_btn.like._like").get_attribute("data-count")
    except Exception:
        return "0"


def parse_comment_contents(post, id):
    comment_list = post.find_elements(by=By.CLASS_NAME, value="reply.reply_dived.clear.reply_replieable._post")
    for comment_item in comment_list:
        com = comment_item.find_element(by=By.CLASS_NAME, value="reply_content")
        try:
            com_txt = com.find_element(by=By.CLASS_NAME, value="reply_text")
            try:
                author = com.find_element(by=By.CLASS_NAME, value="author")
                comment_dict['comment_author_profile_url'] = author.get_attribute("href")
                comment_dict['comment_author_name'] = author.text
            except Exception as e:
                logging.warning(f"Failed to establish the author of a comment. Error: {e}")
                comment_dict['comment_author_profile_url'] = ""
                comment_dict['comment_author_name'] = ""

            comment_dict['post_id'] = post.find_element(by=By.CLASS_NAME, value="wall_post_cont._wall_post_cont").get_attribute("id")
            comment_dict['comment_id'] = comment_item.get_attribute("id")
            comment_dict['comment_text'] = com_txt.text
            comment_dict['comment_likes_count'] = count_likes(com)
            comment_dict['comment_date'] = com.find_element(by=By.CLASS_NAME, value="reply_date").text
            comment_dict['created_at'] = str(datetime.datetime.now())
            write_to_file(comment_dict, id)
        except Exception as e:
            logging.warning(f"Failed to add information about the comment. Error: {e}")
            continue


def add_all_cookies_to_session():
    for cookie in read_stored_cookies():
        try:
            driver.add_cookie(cookie)
            logging.debug(f"Successfully added a cookie: {cookie}")
        except Exception as err:
            logging.error(f"Failed to add a cookie: {cookie}.\n Error message: {err}")


def read_stored_cookies():
    with open("cookies.json", "r") as cookie_file:
        return json.load(cookie_file)


if __name__ == '__main__':
    base_url = "https://vk.com/"
    id_list = re.split("\n", """public123915905
public34491673
public45064245
public25554967
public23433159
public66678575
public22741624
public45745333
public30022666""")
# """interestplanet_ru""")
# """public28477986
# public57846937
# public12382740
# public31836774
# public23064236
# public29246653
# public56106344
# public40567146
# public43776215
# public40498005
# public26750264
# public30179569
# public36164349
# public48319873
# public113071474
# public26669118
# public38683579
# public39009769
# public33769500
# public39728801
# public19802817""")
    project_path = f"{os.getcwd()}/results_selenium"
    chrome_options = webdriver.ChromeOptions()
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(chrome_options=chrome_options)
    # add_all_cookies_to_session()
    comment_dict = {}
    post_ids = set()
    
    for id in id_list:
        failed_attempts = 0
        driver.get(f"{base_url}{id}")
        scroll_once(wait_time=3)
        # fill_login_form()
        time.sleep(30)

        while failed_attempts <= 2:
            try:
                for pst in parse_post_contents():
                    unfold_all_comments(pst, id)
                failed_attempts += 1

            except Exception as e:
                logging.warning(f"Failed to get the page from the id_list. Error: {e}")
                failed_attempts += 1