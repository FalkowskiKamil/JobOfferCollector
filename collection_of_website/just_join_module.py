import re
from time import sleep
from datetime import date, timedelta
from bs4 import BeautifulSoup
from selenium import webdriver

from base_module import BaseSite, NewsOffert

class Just_join(BaseSite):
    __tablename__ = "Just_join"


def just_join_function(session):
    # Decrement deadline
    just_join = Just_join()
    just_join.decrement_deadline(session)
    
    # Scrapping data
    driver = webdriver.Chrome()
    driver.get(
        "https://justjoin.it/all/python/junior"
    )
    sleep(2)
    html = driver.page_source
    driver.close()
    soup = BeautifulSoup(html, "html.parser")
    results = soup.find_all("div",{"class":"jss239 jss236"})
    root_site = "https://justjoin.it"

    # Iterating over offert
    for result in results:
        link = root_site + result.find_parent("div").find("a")["href"]
        # Checking if offert already exist in database
        offer_exist_in_db = (
                session.query(Just_join).filter(Just_join.link == link).count()
            )
        if offer_exist_in_db > 0:
            continue
        else:
            # Scrapping details
            time = result.find("div",{"class":"jss249"}).get_text()
            if time == "New":
                time = date.today()
            else:
                # Calculating made of data
                pattern = r"\d+"
                days_ago = int(re.findall(pattern, time)[0]) 
                time = date.today() - timedelta(days=days_ago)
            title = result.find("div",{"class":"jss246"}).get_text()
            company = result.find("div",{"class":"jss252"}).get_text()
            location = result.find("div",{"class":"jss253"}).get_text()
            #Checking remote
            if "Fully Remote" in location:
                remote = True
            else:
                remote = False
            location = location.split(",")[0]
            wages = result.find("div",{"class":"jss263"}).get_text()
        # Saving detail
            new_just_join = Just_join(
                    time=time,
                    offer_title=title,
                    company_name=company,
                    location=location,
                    wages=wages,
                    link=link,
                    remote=remote,
                )
            new_offer = NewsOffert(
                    time=time,
                    offer_title=title,
                    company_name=company,
                    location=location,
                    wages=wages,
                    link=link,
                    remote=remote,
                    source="Just Join",
                )
            session.add_all([new_just_join, new_offer])