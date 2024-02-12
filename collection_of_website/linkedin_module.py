from time import sleep
import math
from datetime import date, timedelta

from bs4 import BeautifulSoup
from sqlalchemy import Column, String
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from collection_of_website.base_module import BaseSite, NewsOffert, find_digit, title_checker


class Linkedin(BaseSite):
    __tablename__ = "Linkedin"
    offert_id = Column(String, unique=True)


def linkedin_function(session):
    # Decrement deadline
    linkedin = Linkedin()
    linkedin.decrement_deadline(session)
    
    # Init Selenium Driver
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36")
    driver = webdriver.Chrome(options=options)

    # Scrapping offert
    driver.get("https://www.linkedin.com/jobs/search/?keywords=Python&location=Warszawa%20i%20okolice&locationId=&geoId=90009828&f_TPR=r604800&f_PP=102560051&f_E=1%2C2&f_WT=1%2C3%2C2&position=1&pageNum=0")
    sleep(1)
    number_of_offert_text = driver.find_element(By.XPATH, "/html/body/div[3]/div/main/div/h1/span[1]").text
    number_of_offert = find_digit(number_of_offert_text)
    
    # Checking count of scrolling
    if number_of_offert > 25:
        if number_of_offert < 160:
            scrolling_count = math.ceil(number_of_offert / 30) - 1
        else:
            scrolling_count = 7

        # Scrolling part
        for _ in range(scrolling_count):
            driver.execute_script("window.scrollBy(0,document.body.scrollHeight)")
            sleep(1)

        # Calculating count of button
        if number_of_offert > 160:
            number_of_pages = math.ceil((number_of_offert - 160) / 25)+1

            # Closing loggin and newsletter div
            try:
                element = WebDriverWait(driver, 2).until(ec.element_to_be_clickable((By.XPATH, '/html/body/div[6]/button')))
                element.click()
            except:
                number_of_pages += 1
            try:
                element2 = WebDriverWait(driver, 2).until(ec.element_to_be_clickable((By.XPATH, '/html/body/div[5]/button')))
                element2.click()
            except:
                number_of_pages += 1

            # Button part
            for page in range(number_of_pages):
                try:
                    driver.execute_script("window.scrollBy(0,document.body.scrollHeight)")
                    element = WebDriverWait(driver, 2).until(ec.element_to_be_clickable((By.XPATH, '/html/body/div[3]/div/main/section[2]/button')))
                    element.click()
                    sleep(2)
                except:
                    continue
            driver.execute_script("window.scrollBy(0,document.body.scrollHeight)")

    # Scrapping full-page
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    results = soup.find_all("div", {"class": "base-card relative w-full hover:no-underline focus:no-underline base-card--link base-search-card base-search-card--link job-search-card"})
    driver.close()
    existing_data = [int(entry.offert_id) for entry in session.query(Linkedin).all()]
    # Collecting details
    for result in results:
        offert_id = int(find_digit(result.get("data-entity-urn")))
        link = (result.find("a", {"class": "base-card__full-link"}).get("href")).strip()

        # Checking if offer already exist in database
        if offert_id in existing_data:
            continue
        else:
            existing_data.append(offert_id)
            company = (result.find("h4", {"class": "base-search-card__subtitle"}).get_text()).strip()
            title = (result.find("h3", {"class": "base-search-card__title"}).get_text()).strip()
            title_check = title_checker(title)
            if title_check is True:
                continue
            location = (result.find("span", {"class": "job-search-card__location"}).get_text()).strip()

            # Transform date
            try:
                days_ago = find_digit((result.find("time", {"class": "job-search-card__listdate"}).get_text()).strip())
                time = date.today() - timedelta(days=days_ago)
            except:
                time = date.today()

            # Saving data
            new_linked = Linkedin(
                offert_id=offert_id,
                time=time,
                offer_title=title,
                company_name=company,
                location=location,
                link=link,)
            
            new_offer = NewsOffert(
                offer_title=title,
                company_name=company,
                location=location,
                link=link,
                source="linked")
            session.add_all([new_linked, new_offer])
