import os

import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup

from github import Github


chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")

chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")

driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)


def parse_user_meta(driver, usr_url):
    result = {'user_profile': usr_url}

    try:
        driver.get(usr_url)
    except:
        return result

    soup = BeautifulSoup(driver.page_source, "html.parser")

    table = soup.find_all('div', {'class': 'cuCIV _R _c _n z'})

    for tb in table:
        spans = tb.find_all('span')
        result[spans[0].text] = spans[1].text

    return result


reviews = pd.read_csv('reviews_dedup.csv')
uniques_profiles = reviews.user_profile.unique()

uniques_profiles_meta_lst = list(map(lambda x: parse_user_meta(driver, x), uniques_profiles[:5]))

uniques_profiles_meta_df = pd.DataFrame(uniques_profiles_meta_lst)

github = Github(os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN"))
repository = github.get_user().get_repo(os.environ.get('REPOSITORY_NAME'))

filename = 'files/uniques_profiles_meta_df.json'

try:
    file = repository.create_file(filename, "create_file via PyGithub", uniques_profiles_meta_df.to_json())
except:
    file_content = repository.get_contents(filename)
    file = repository.update_file(filename, "update_file via PyGithub", uniques_profiles_meta_df.to_json(),
                                  file_content.sha
                                  )

