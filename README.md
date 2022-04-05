## VK selenium comment scraper

Keep in mind: this script makes use of the chrome webdriver. Please install both **[Google Chrome browser](https://www.google.com/chrome/)** and **[Chrome webdriver](https://chromedriver.chromium.org/downloads)** before running it.

### Functions of the script
- walks through a list of communities / public accounts
- walks down throught each post on the page
  - recursively unfolds comments under each post till the last comment under the post is reached
  - parses the contents of all comments under the post:
    - comment author:
      - pforile url
      - full name
    - ID of the post, under which the comment was left
    - ID of the comment
    - content of the comment (text)
    - count of likes
    - datetime of the comment creation
    - datetime of the extraction by the scraper
  - writes the data out line by line to a .json file
- once there's no more posts proceeds to the next community / page on the list

