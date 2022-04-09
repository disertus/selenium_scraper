import datetime
import json
import logging
import os
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By

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
                if com.text == "Show more comments" or com.text == "Show next comment":
                    # scrolls directly to the coordinates of a comment on the page
                    driver.execute_script(f'window.scrollTo({com.location["x"]}, {com.location["y"] - 70});')
                    com.click()
                    time.sleep(2)
                    parse_comment_contents(post, id, comment_ids)
                else:
                    driver.execute_script(f'window.scrollTo({com.location["x"]}, {com.location["y"] - 70});')
                    parse_comment_contents(post, id, comment_ids)
                    continue
            unfold_all_comments(post, id, comment_ids)
        else:
            driver.execute_script(f'window.scrollTo({post.location["x"]}, {post.location["y"]});')
            time.sleep(2)
            parse_comment_contents(post, id, comment_ids)
    except Exception as e:
        logging.warning(f"Did not find any comments to unfold. Error: {e}")
        parse_comment_contents(post, id, comment_ids)


def parse_post_contents(driver_instance, post_id_list):
    posts = driver_instance.find_elements(by=By.CLASS_NAME, value="post_content")
    for post in posts:
        if post.id not in post_id_list:
            post_ids.add(post.id)
            yield post
        else:
            continue


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
    id_list = re.split("\n", """public57846937""")
# public56106344
# public25554967
# public39009769
# public22741624
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
# public12382740
# public31836774
# public23064236
# public29246653
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
    chrome_options.add_experimental_option("prefs", prefs)
    # chrome_options.add_argument("--headless")

    # todo: put the path to the webdriver into the project folder
    # todo: check if the post's date exceeds 20 Feb,
    driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.maximize_window()
    # add_all_cookies_to_session()
    comment_dict = {}
    post_ids = set()

    for id in id_list:
        batch_number = 0
        driver.get(f"{base_url}{id}")
        scroll_once(wait_time=3)
        login_to_profile.fill_login_form(drive_instance=driver)
        time.sleep(3)

        comment_ids = set()
        while 1:
            try:
                batch_start = time.time()
                for pst in parse_post_contents(driver_instance=driver, post_id_list=post_ids):
                    print(f"Parsing post comments for post {pst.id}.")
                    unfold_all_comments(pst, id, comment_ids)
                    # if (post_list.index(pst) + 1) % 10 == 0:
                        # scroll_once(3)
                batch_end = time.time()
                batch_number += 1
                print(f"\nParsed posts {batch_number * 10}.")
                print(f"Batch was parsed in: {batch_end - batch_start} seconds.")

            except Exception as e:
                logging.warning(f"Failed to get the page from the id_list. Error: {e}")
                batch_number += 1
