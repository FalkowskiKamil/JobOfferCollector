import re
import requests
from time import sleep
from datetime import date, timedelta
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from sqlalchemy import inspect
from sqlalchemy.orm import sessionmaker

from base_module import BaseSite, NewsOffert, Base, engine


class Just_join(BaseSite):
    __tablename__ = "Just_join"


def just_join_function():
    # Connect to Database
    inspector = inspect(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Checking if table exists
    if not inspector.has_table(Just_join.__tablename__):
        Base.metadata.create_all(engine)
    else:
        # Decrement deadline
        just_join = Just_join()
        just_join.decrement_deadline(session)
    
 
    driver = webdriver.Chrome()
    driver.get(
        "https://justjoin.it/all/python/junior"
    )
    sleep(2)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    results = soup.find_all("div",{"class":"jss239 jss236"})
    root_site = "https://justjoin.it"
    for offert in results:
        link_parent_div = offert.find_parent("div")
        link_a = link_parent_div.find("a")
        link_offert = link_a.get("href")
        link = root_site + link_offert
        offer_exist_in_db = (
                session.query(Just_join).filter(Just_join.link == link).count()
            )
        if offer_exist_in_db > 0:
            continue
        else:
            time = offert.find("div",{"class":"jss249"}).get_text()
            if time == "New":
                time = date.today()
            else:
                pattern = r"\d+"
                days_ago = int(re.findall(pattern, time)[0])  # Zamień wynik na liczbę całkowitą
                time = date.today() - timedelta(days=days_ago)
            title = offert.find("div",{"class":"jss246"}).get_text()
            company = offert.find("div",{"class":"jss252"}).get_text()
            location = offert.find("div",{"class":"jss253"}).get_text()
            if "Fully Remote" in location:
                remote = True
            else:
                remote = False
            location = location.split(",")[0]
            wages = offert.find("div",{"class":"jss263"}).get_text()
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
    session.commit()
    session.close()