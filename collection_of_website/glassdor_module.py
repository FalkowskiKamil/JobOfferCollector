from time import sleep
from datetime import date, timedelta
import math

from bs4 import BeautifulSoup
from sqlalchemy import Column, String
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from collection_of_website.base_module import (
    BaseSite,
    NewsOffert,
    create_table,
    find_digit,
    title_checker,
)


class Glassdor(BaseSite):
    __tablename__ = "Glassdor"
    offert_id = Column(String)


def glassdor_function(session, inspector):
    if not inspector.has_table(Glassdor.__tablename__):
        session, inspector = create_table(session)

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
        "https://www.glassdoor.com/Job/warsaw-junior-python-jobs-SRCH_IL.0,6_IC3094484_KO7,20.html?fromAge=7&sortBy=date_desc&radius=50"
    )
    cookies = WebDriverWait(driver, 5).until(
        ec.element_to_be_clickable((By.XPATH, '//*[@id="onetrust-accept-btn-handler"]'))
    )
    if cookies:
        cookies.click()
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    # Iterate over pages
    number_of_offert = find_digit(
        soup.find("h1", {"class": "SearchResultsHeader_jobCount__12dWB"}).get_text()
    )

    number_of_pages = math.ceil(int(number_of_offert) / 20)
    if number_of_pages > 1:
        for page in range(number_of_pages):
            try:
                driver = next_page(driver)
            finally:
                sleep(2)
                continue

    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    results = soup.find_all("li", {"class": "JobsList_jobListItem__JBBUV"})
    results.pop()
    driver.close()

    existing_data = [entry.offert_id for entry in session.query(Glassdor).all()]
    # Collecting details
    index = 0
    for result in results:
        index += 1
        data_id = result.get("data-jobid")
        # Checking if offer already exist in database
        if data_id in existing_data:
            continue
        else:
            link = result.find("a").get("href")

            days_ago = find_digit(
                result.find("div", {"data-test": "job-age"}).get_text()
            )
            if days_ago > 10:
                days_ago = 1
            time = date.today() - timedelta(days=days_ago)
            title = result.find("a", {"class": "JobCard_seoLink__WdqHZ"}).get_text()
            title_check = title_checker(title)
            if title_check is True:
                continue
            try:
                company = result.find(
                    "div",
                    {
                        "class": "EmployerProfile_employerInfo__GaPbq EmployerProfile_employerWithLogo__R_rOX"
                    },
                ).get_text()
            except:
                company = result.find("div", {"class": "css-8wag7x"}).get_text()
            location = result.find(
                "div", {"class": "JobCard_location__N_iYE"}
            ).get_text()

            # Saving data
            new_glassdor = Glassdor(
                offert_id=id,
                time=time,
                offer_title=title,
                company_name=company,
                location=location,
                link=link,
            )

            new_offer = NewsOffert(
                offer_title=title,
                company_name=company,
                location=location,
                link=link,
                source="glassdor",
            )

            session.add_all([new_glassdor, new_offer])
    return session


def next_page(driver):
    try:
        sleep(1)
        driver.execute_script("window.scrollBy(0,document.body.scrollHeight)")
        next_site_button = WebDriverWait(driver, 5).until(
            ec.element_to_be_clickable(
                (
                    By.XPATH,
                    "/html/body/div[2]/div[1]/div[3]/div[2]/div[1]/div[2]/div/button",
                )
            )
        )
        next_site_button.click()
        return driver
    finally:
        sleep(2)
        loggin_button = WebDriverWait(driver, 2).until(
            ec.element_to_be_clickable(
                (By.XPATH, '//*[@id="LoginModal"]/div/div/div/div[2]/button')
            )
        )
        loggin_button.click()
        return next_page(driver)
