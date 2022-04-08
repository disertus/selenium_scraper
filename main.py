import datetime
import json
import logging
import os
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import element_to_be_clickable

from profile_login import login_to_profile
# from selenium.webdriver.chrome.options import Options
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


def unfold_all_comments(post, id, comment_ids):
    temp_set = set()
    try:
        temp_set.clear()
        comments_list = post.find_elements(by=By.CLASS_NAME, value="js-replies_next_label")
        [temp_set.add(item.text) for item in comments_list]
        if "Show more comments" in temp_set or "Show next comment" in temp_set:
            for com in comments_list:
                coordinates = com.location_once_scrolled_into_view  # returns dict of X, Y coordinates
                if com.text == "Show more comments" or com.text == "Show next comment":
                    # scrolls directly to the coordinates of a comment on the page
                    driver.execute_script(f'window.scrollTo({coordinates["x"]}, {coordinates["y"]});')
                    com.click()
                    time.sleep(1.5)
                    parse_comment_contents(post, id, comment_ids)
                else:
                    driver.execute_script(f'window.scrollTo({coordinates["x"]}, {coordinates["y"]});')
                    parse_comment_contents(post, id, comment_ids)
                    continue
            unfold_all_comments(post, id, comment_ids)
        else:
            parse_comment_contents(post, id, comment_ids)
    except Exception as e:
        logging.warning(f"Did not find any comments to unfold. Error: {e}")
        parse_comment_contents(post, id, comment_ids)


def parse_post_contents(driver_instance):
    posts = driver_instance.find_elements(by=By.CLASS_NAME, value="post_content")
    for post in posts[-10:]:
        yield post


def count_likes(reply_content):
    try:
        return reply_content.find_element(by=By.CLASS_NAME, value="like_btn.like._like").get_attribute("data-count")
    except Exception:
        return "0"


def parse_comment_contents(post, id, comment_ids: set):
    comment_list = post.find_elements(by=By.CLASS_NAME, value="reply.reply_dived.clear.reply_replieable._post")
    for comment_item in comment_list:
        com = comment_item.find_element(by=By.CLASS_NAME, value="reply_content")
        if comment_item.get_attribute("id") in comment_ids:
            continue
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
        comment_ids.add(comment_dict['comment_id'])
        write_to_file(comment_dict, id)


if __name__ == '__main__':
    base_url = "https://vk.com/"
    id_list = re.split("\n", """public39009769""")
# public22741624
# public25554967
# public40567146
# public39728801
# public38683579
# public45064245
# public12648877
# public123915905
# public34491673
# public23433159
# public66678575
# public45745333
# public30022666
# interestplanet_ru
# public28477986
# public57846937
# public12382740
# public31836774
# public23064236
# public29246653
# public56106344
# public43776215
# public40498005
# public26750264
# public30179569
# public36164349
# public48319873
# public113071474
# public26669118
# public33769500
# public19802817""")
    project_path = f"{os.getcwd()}/results_selenium/refactored_script"
    chrome_options = webdriver.ChromeOptions()
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_experimental_option("prefs", prefs)

    # todo: put the path to the webdriver into the project folder
    driver = webdriver.Chrome(chrome_options=chrome_options)
    # add_all_cookies_to_session()
    comment_dict = {}

    for id in id_list:
        failed_attempts = 0
        driver.get(f"{base_url}{id}")
        scroll_once(wait_time=3)
        login_to_profile.fill_login_form(drive_instance=driver)
        time.sleep(3)

        comment_ids = set()
        while 1:
            try:
                for pst in parse_post_contents(driver_instance=driver):
                    post_list = driver.find_elements(by=By.CLASS_NAME, value="post_content")
                    unfold_all_comments(pst, id, comment_ids)
                    # if (post_list.index(pst) + 1) % 10 == 0:
                        # scroll_once(3)
                failed_attempts += 1

            except Exception as e:
                logging.warning(f"Failed to get the page from the id_list. Error: {e}")
                failed_attempts += 1
