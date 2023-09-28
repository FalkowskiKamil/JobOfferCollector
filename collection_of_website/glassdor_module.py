from time import sleep
from datetime import date, timedelta
import math

from bs4 import BeautifulSoup
from sqlalchemy import Column, String
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from collection_of_website.base_module import (
    BaseSite,
    NewsOffert,
    find_digit,
    title_checker,
)


class Glassdor(BaseSite):
    __tablename__ = "Glassdor"
    offert_id = Column(String)


def glassdor_function(session):
    # Decrement deadline
    glassdor = Glassdor()
    glassdor.decrement_deadline(session)

    # Init Selenium Driver
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
    )
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(500, 1000)
    # Scrapping offert
    driver.get(
        "https://www.glassdoor.com/Job/warsaw-junior-python-jobs-SRCH_IL.0,6_IC3094484_KO7,20.html"
    )
    cookies = WebDriverWait(driver, 4).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="onetrust-accept-btn-handler"]'))
    )
    cookies.click()
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    root_link = "https://www.glassdoor.com"

    # Iterate over pages
    number_of_offert = find_digit(
        soup.find("h1", {"class": "SearchResultsHeader_jobCount__12dWB"}).get_text()
    )
    
    number_of_pages = math.ceil(int(number_of_offert) / 20)
    for page in range(number_of_pages):
        try:
            driver = next_page(driver)
        except:
            sleep(2)
            continue
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    results = soup.find_all("li", {"class": "JobsList_jobListItem__JBBUV"})
    driver.close()
    # Collecting details
    for result in results:
        id = result.get("data-jobid")
        # Checking if offer already exist in database
        offer_exist_in_db = (
            session.query(Glassdor).filter(Glassdor.offert_id == id).count()
        )
        if offer_exist_in_db > 0:
            continue
        else:
            link = root_link + result.find("a").get("href")
            days_ago = find_digit(
                result.find(
                    "div", {"class": "d-flex align-items-end ml-xsm listing-age"}
                ).get_text()
            )
            if days_ago > 28:
                continue
            time = date.today() - timedelta(days=days_ago)
            title = result.find("a", {"class": "css-1nh9iuj"}).get_text()
            title_check = title_checker(title)
            if title_check == True:
                continue
            try:
                company = result.find("div", {"class": "job-search-8wag7x"}).get_text()
            except:
                company = result.find("div", {"class": "css-8wag7x"}).get_text()
            location = result.find("div", {"class": "location mt-xxsm"}).get_text()
            try:
                wages = result.find("div", {"class": "salary-estimate"}).get_text()
            except:
                wages = None
            # Saving data
            new_glassdor = Glassdor(
                offert_id=id,
                time=time,
                offer_title=title,
                company_name=company,
                location=location,
                wages=wages,
                link=link,
            )

            new_offer = NewsOffert(
                time=time,
                offer_title=title,
                company_name=company,
                location=location,
                wages=wages,
                link=link,
                source="Glassdor",
            )

            session.add_all([new_glassdor, new_offer])


def next_page(driver):
    try:
        sleep(1)
        driver.execute_script("window.scrollBy(0,document.body.scrollHeight)")
        next_site_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "/html/body/div[2]/div[1]/div[3]/div[2]/div[1]/div[2]/div/button",
                )
            )
        )
        next_site_button.click()
        return driver
    except:
        sleep(2)
        loggin_button = WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="LoginModal"]/div/div/div/div[2]/button')
            )
        )
        loggin_button.click()
        return next_page(driver)
