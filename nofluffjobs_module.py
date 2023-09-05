from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from sqlalchemy import inspect
from sqlalchemy.orm import sessionmaker

from base_module import BaseSite, NewsOffert, Base, engine


class Nofluffjobs(BaseSite):
    __tablename__ = "NoFluffJobs"


def nofluffjobs_function():
    # Connect to Database
    inspector = inspect(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Checking if table exists
    if not inspector.has_table(Nofluffjobs.__tablename__):
        Base.metadata.create_all(engine)
    else:
        # Decrement deadline
        nofluffjobs = Nofluffjobs()
        nofluffjobs.decrement_deadline(session)

    # Scrapping data
    driver = webdriver.Chrome()
    driver.get(
        "https://nofluffjobs.com/pl/praca-zdalna/Python?page=1&criteria=city%3Dwarszawa%20%20seniority%3Dtrainee,junior"
    )
    sleep(2)
    accept_cookies(driver)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    container = soup.find("div", {"class": "list-container ng-star-inserted"})
    total_results = container.find_all("a", {"class": "posting-list-item"})

    # Calculating number of site
    number_of_site_ul = soup.find("ul", {"class": "pagination mb-0 ng-star-inserted"})
    number_of_site = number_of_site_ul.find_all("li")
    number_of_site = int(list(number_of_site)[-2].get_text().strip())

    # Iterating over sites
    for site in range(number_of_site - 1):
        driver = next_page(driver)
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        container = soup.find("div", {"class": "list-container ng-star-inserted"})
        results_next_page = container.find_all("a", {"class": "posting-list-item"})
        total_results += results_next_page
    root_site = "https://nofluffjobs.com"

    # Transform given data
    for result in total_results:
        link = result.get("href")
        link = root_site + link
        # Checking if offer already exist in database
        offer_exist_in_db = (
            session.query(Nofluffjobs).filter(Nofluffjobs.link == link).count()
        )
        if offer_exist_in_db > 0:
            continue
        else:
            title = result.find(
                "h3",
                {"class": "posting-title__position text-truncate ng-star-inserted"},
            ).get_text()
            company = result.find(
                "span",
                {"class": "d-block tw-text-xs text-truncate font-gray-757575 company"},
            ).get_text()
            place = result.find(
                "span",
                {
                    "class": "tw-text-ellipsis tw-inline-block tw-overflow-hidden tw-whitespace-nowrap lg:tw-max-w-[100px] tw-text-right"
                },
            ).get_text()
            wages = result.find(
                "span",
                {
                    "class": "text-truncate badgy salary tw-btn tw-btn-secondary-outline tw-btn-xs ng-star-inserted"
                },
            ).get_text()
            remote = False
            if place == " Zdalnie ":
                remote = True
            new_nofluffjobs = Nofluffjobs(
                offer_title=title,
                company_name=company,
                location=place,
                wages=wages,
                link=link,
                remote=remote,
            )

            new_offer = NewsOffert(
                offer_title=title,
                company_name=company,
                location=place,
                wages=wages,
                link=link,
                remote=remote,
                source="NoFluffJobs",
            )
            session.add_all([new_nofluffjobs, new_offer])
    session.commit()
    session.close()


def accept_cookies(driver):
    cookie_button = driver.find_element(By.ID, "onetrust-accept-btn-handler")
    sleep(2)
    cookie_button.click()
    sleep(2)


def next_page(driver):
    next_page_button = driver.find_element(
        By.XPATH,
        "(/html/body/nfj-root/nfj-layout/nfj-main-content/div/nfj-postings-search/div/common-main-loader/nfj-search-results/div/nfj-pagination/ul/li/a)[last()]",
    )
    sleep(1)
    driver.execute_script("arguments[0].scrollIntoView();", next_page_button)
    driver.execute_script(f"window.scrollBy(0, -100);")
    sleep(1)
    next_page_button.click()
    sleep(2)
    return driver
