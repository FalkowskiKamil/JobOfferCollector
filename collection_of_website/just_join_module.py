from datetime import date, timedelta

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from collection_of_website.base_module import BaseSite, NewsOffert, find_digit


class Just_join(BaseSite):
    __tablename__ = "Just Join"


def just_join_function(session):
    # Decrement deadline
    just_join = Just_join()
    just_join.decrement_deadline(session)

    # Init Selenium Driver
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36")
    driver = webdriver.Chrome(options=options)

    # Scrapping data
    driver.get("https://justjoin.it/all/python/junior")
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    results = soup.find_all("div", {"class": "jss239 jss236"})
    root_site = "https://justjoin.it"
    driver.close()

    # Collecting details
    for result in results:
        link = root_site + result.find_parent("div").find("a")["href"]

        # Checking if offert already exist in database
        offer_exist_in_db = (
            session.query(Just_join).filter(Just_join.link == link).count()
        )
        if offer_exist_in_db > 0:
            continue
        else:
            # Transform date
            time = result.find("div", {"class": "jss249"}).get_text()
            if time == "New":
                time = date.today()
            else:
                days_ago = find_digit(time)
                time = date.today() - timedelta(days=days_ago)
            title = result.find("div", {"class": "jss246"}).get_text()
            company = result.find("div", {"class": "jss252"}).get_text()
            location = result.find("div", {"class": "jss253"}).get_text()
            if "Fully Remote" in location:
                remote = True
            else:
                remote = False
            location = location.split(",")[0]
            wages = result.find("div", {"class": "jss263"}).get_text()

            # Saving data
            new_just_join = Just_join(
                time=time,
                offer_title=title,
                company_name=company,
                location=location,
                wages=wages,
                link=link,
                remote=remote)
            
            new_offer = NewsOffert(
                time=time,
                offer_title=title,
                company_name=company,
                location=location,
                wages=wages,
                link=link,
                remote=remote,
                source="Just Join")
            session.add_all([new_just_join, new_offer])
