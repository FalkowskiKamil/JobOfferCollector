from datetime import date, timedelta
from bs4 import BeautifulSoup
from selenium import webdriver
from sqlalchemy import Column, String
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from collection_of_website.base_module import BaseSite, NewsOffert, find_digit


class Glassdor(BaseSite):
    __tablename__ = "Glassdor"
    offert_id = Column(String)


def glassdor_function(session):
    glassdor = Glassdor()
    glassdor.decrement_deadline(session)

    driver = webdriver.Chrome()
    driver.get(
        "https://www.glassdoor.com/Job/warsaw-junior-python-jobs-SRCH_IL.0,6_IC3094484_KO7,20.htm"
    )
    driver = accept_cookies(driver)
    html = driver.page_source

    soup = BeautifulSoup(html, "html.parser")
    results = soup.find_all(
        "a", {"class": "d-flex justify-content-between p-std jobCard"}
    )
    number_of_pages_text = soup.find("div", {"class": "paginationFooter"}).get_text()
    number_of_pages = int(number_of_pages_text[-2:].strip())-1
    for page in range(number_of_pages - 1):
        driver = next_page(driver)
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        results += soup.find_all(
            "a", {"class": "d-flex justify-content-between p-std jobCard"}
        )
    driver.close()

    root_link = "https://www.glassdoor.com"

    for result in results:
        link = root_link + result.get("href")
        result_parent = result.find_parent("li")
        id = result_parent.get("data-id")

        # Checking if offer already exist in database
        offer_exist_in_db = (
            session.query(Glassdor).filter(Glassdor.offert_id == id).count()
        )
        if offer_exist_in_db > 0:
            continue
        else:
            days_ago = find_digit(
                result.find(
                    "div", {"class": "d-flex align-items-end ml-xsm listing-age"}
                ).get_text()
            )
            time = date.today() - timedelta(days=days_ago)
            title = result.find("div", {"class": "job-title"}).get_text()
            try:
                company = result.find("div", {"class": "job-search-8wag7x"}).get_text()
            except:
                company = result.find("div", {"class": "css-8wag7x"}).get_text()
            location = result.find("div", {"class": "location mt-xxsm"}).get_text()
            wages = result.find("div", {"class": "salary-estimate"})
            if wages:
                wages = wages.get_text()
            remote = False

            # Saving details
            new_glassdor = Glassdor(
                offert_id=id,
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
                source="glassdor",
            )
            session.add_all([new_glassdor, new_offer])


def accept_cookies(driver):
    cookies = WebDriverWait(driver, 2).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="onetrust-accept-btn-handler"]'))
    )
    cookies.click()
    return driver


def next_page(driver):
    try:
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        next_site_button = WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "/html/body/div[2]/div[2]/div/div/div/div/section/article/div[2]/div/div[1]/button[6]",
                )
            )
        )
        next_site_button.click()
        return driver
    except:
        loggin_button = WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="LoginModal"]/div/div/div/div[2]/button')
            )
        )
        loggin_button.click()
        return next_page(driver)
