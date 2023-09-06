import re
import requests
from time import sleep
from datetime import date
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from sqlalchemy import inspect
from sqlalchemy.orm import sessionmaker

from base_module import BaseSite, NewsOffert, Base, engine


class Pracuj(BaseSite):
    __tablename__ = "Pracuj.pl"


def pracuj_function():
    # Connect to Database
    inspector = inspect(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Checking if table exists
    if not inspector.has_table(Pracuj.__tablename__):
        Base.metadata.create_all(engine)
    else:
        # Decrement deadline
        pracuj = Pracuj()
        # olx.decrement_deadline(session)

    driver = webdriver.Chrome()
    driver.get(
        "https://www.pracuj.pl/praca/python;kw/warszawa;wp?rd=30&cc=5016001%2C5016002%2C5016003%2C5016004%2C5001%2C5002%2C5003%2C5004%2C5005%2C5006%2C5037%2C5036%2C5007%2C5008%2C5009%2C5010%2C5011%2C5015%2C5014%2C5013%2C5012%2C5035%2C5033%2C5032%2C5031%2C5028%2C5027%2C5025%2C5026%2C5024%2C5023%2C5022%2C5021%2C5020%2C5019%2C5018%2C5017%2C5034&et=1%2C17"
    )
    sleep(2)
    accept_cookies(driver)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    number_of_offert = soup.find("span", {"class": "listing_jebwd19"}).get_text()
    pattern = r"\d+"
    number_of_offert = re.findall(pattern, number_of_offert)
    page_number = soup.find("div", {"class": "listing_w1sj4gb8"}).get_text()
    page_number = re.findall(pattern, page_number)
    section_offers = soup.find("div", {"data-test": "section-offers"})
    total_result = section_offers.find_all(
        "div", {"class": "listing_b1evff58 listing_po9665q"}
    )
    for page in range(int(page_number[0]) - 1):
        driver = next_page(driver)
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        section_offers = soup.find("div", {"data-test": "section-offers"})
        result = section_offers.find_all(
            "div", {"class": "listing_b1evff58 listing_po9665q"}
        )
        total_result += result

    driver.close()
    for offert in total_result:
        try:
            try:
                link = offert.find("a", {"class": "listing_o1dyw02w"}).get("href")
            except:
                ...
            if "%s" in link or "?s" in link:
                link = link.split("?s")[0]
            offer_exist_in_db = (
                session.query(Pracuj).filter(Pracuj.link == link).count()
            )
            if offer_exist_in_db > 0:
                continue
            else:
                time = offert.find(
                    "p",
                    {
                        "class": "listing_b1nrtp6c listing_pk4iags size-caption listing_t1rst47b"
                    },
                ).get_text()

                time = time.removeprefix("Opublikowana: ")
                title = offert.find(
                    "a", {"class": "listing_o1dyw02w listing_n194fgoq"}
                ).get_text()
                company = offert.find(
                    "h4", {"class": "listing_eiims5z size-caption listing_t1rst47b"}
                ).get_text()
                try:
                    location = offert.find(
                        "h5", {"class": "listing_rdl5oe8 size-caption listing_t1rst47b"}
                    ).get_text()
                except:
                    location = offert.find("strong").get_text()
                try:
                    wages = offert.find("span", {"class": "listing_sug0jpb"}).get_text()
                except:
                    wages = "NaN"
                remote = False
                additional_information = offert.find_all(
                    "li", {"class": "listing_isg28kc"}
                )
                for information in additional_information:
                    if information.get_text() == "Praca zdalna":
                        remote = True
                        break

            new_pracuj = Pracuj(
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
                source="Pracuj.pl",
            )
            session.add_all([new_pracuj, new_offer])
        except:
            print(f"Error 2 =   {link}")
    session.commit()
    session.close()


def accept_cookies(driver):
    cookie_button = driver.find_element(
        By.XPATH, "/html/body/div[1]/div/div[4]/div/div/div/div[3]/div/button[1]"
    )
    sleep(1)
    cookie_button.click()
    sleep(2)


def next_page(driver):
    next_page_button = driver.find_element(
        By.XPATH,
        "/html/body/div[1]/div/div[3]/div[2]/div[1]/div[2]/div[2]/div/div/button[2]",
    )
    sleep(1)
    next_page_button.click()
    sleep(3)
    return driver
