import re
import requests
from time import sleep
from datetime import date, datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from sqlalchemy import inspect
from sqlalchemy.orm import sessionmaker

from base_module import BaseSite, NewsOffert, Base, engine, date_translate


class Olx(BaseSite):
    __tablename__ = "OLX"


def olx_function():
    # Connect to Database
    inspector = inspect(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Checking if table exists
    if not inspector.has_table(Olx.__tablename__):
        Base.metadata.create_all(engine)
    else:
        # Decrement deadline
        olx = Olx()
        olx.decrement_deadline(session)

    # Scrapping init
    driver = webdriver.Chrome()
    driver.get(
        "https://www.olx.pl/praca/q-Python/?page=1"
    )
    sleep(2)
    accept_cookies(driver)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    
    # Checking count of offert
    total_results = soup.find_all("a", {"class": "css-rc5s2u"})
    number_of_offert = soup.find("span", {"data-testid":"total-count"}).get_text()
    pattern = r'\d+'
    number_of_offert = re.findall(pattern, number_of_offert)

    # Calculating next-page count offert
    if int(number_of_offert[0]) > 40:
        number_of_pages = soup.find("ul", {"class": "pagination-list"})
        number_of_pages = list(number_of_pages.find_all("li"))[-1].get_text()
        # Collecting data from next pages
        for page in range(int(number_of_pages.strip()) - 1):
            driver.get(f"https://www.olx.pl/praca/q-Python/?page={page+2}")
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            results = soup.find_all("a", {"class": "css-rc5s2u"})
            total_results += results
    driver.close()

    root_site = "https://www.olx.pl"

    # Iterating over offert
    for result in total_results:
        link = root_site + result.get("href")
        # Checking if data already in db
        offer_exist_in_db = session.query(Olx).filter(Olx.link == link).count()
        if offer_exist_in_db > 0:
            continue
        else:
            # Checking if offert match searching
            if not result.find("p", {"data-testid": "ad-price"}):
                time = result.find("p", {"class":"css-l3c9zc"})
                # Checking if offert match searching #2
                if time:
                    # Clearing date data
                    if "Dzisiaj" in time.get_text():
                        time = date.today()
                    else:
                        # Transfer into date type data
                        if "Odświeżono" in time.get_text():
                            time = time.get_text().removeprefix("Odświeżono dnia ")
                        elif "Dodane" in time.get_text():
                            time = time.get_text().removeprefix("Dodane ")
                        else:
                            time = time.get_text()
                        time = date_translate(time)
                    title = result.find("h6", {"class":"css-1jmx98l"}).get_text()

                    # Getting company name from offert
                    url = requests.get(f"{link}")
                    soup = BeautifulSoup(url.content, "html.parser")
                    company = soup.find("h4", {"class":"css-1lcz6o7"})
                    if company == None:
                        company = soup.find("h4", {"class":"css-qzwsib"})
                    company = company.get_text()
                    location = result.find("span", {"class":"css-d5w927"}).get_text()
                    wages = result.find("p", {"class":"css-1hp12oq"})
                    if wages == None:
                        wages = "NaN"
                    else:
                        wages = wages.get_text()
                    remote = False

                    #Searching of remote-avaibility
                    additional_info = result.find_all("span", {"class":"css-1m53r4k"})
                    for info in additional_info:
                        if info.get_text() == "Praca zdalna dozwolona":
                            remote = True
                            break

                    # Saving data
                    new_olx = Olx(
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
                        source = "Olx"
                    )
                    session.add_all([new_olx, new_offer]) 
    session.commit()
    session.close()
            


def accept_cookies(driver):
    cookie_button = driver.find_element(By.ID, "onetrust-accept-btn-handler")
    sleep(1)
    cookie_button.click()
    sleep(2)