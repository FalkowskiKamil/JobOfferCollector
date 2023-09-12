from time import sleep
import math
from datetime import date, timedelta
from bs4 import BeautifulSoup
from sqlalchemy import Column, String
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from collection_of_website.base_module import BaseSite, NewsOffert, find_digit


class Linkedin(BaseSite):
    __tablename__ = "Linkedin"
    offert_id = Column(String)

def linkedin_function(session):
    # Decrement deadline
    linkedin = Linkedin()
    linkedin.decrement_deadline(session)
    
    # Scrapping init
    driver = webdriver.Chrome()
    driver.get(
        "https://www.linkedin.com/jobs/search/?currentJobId=3630027367&f_E=1%2C2&f_TPR=r604800&geoId=90009828&keywords=Python&location=Warszawa%20i%20okolice&refresh=true&sortBy=R"
    )
    # Scrolling part
    number_of_offert_text = driver.find_element(By.XPATH, "/html/body/div[3]/div/main/div/h1/span[1]").text
    number_of_offert = find_digit(number_of_offert_text)
    if number_of_offert > 25:
        if number_of_offert < 160:
            scrolling_count = math.ceil(number_of_offert / 30) - 1
        else:
            scrolling_count = 7
        for _ in range(scrolling_count):
            driver.execute_script("window.scrollBy(0,document.body.scrollHeight)")
            sleep(1)
        # Button-refreshment part
        if number_of_offert > 160:
            number_of_pages = math.ceil((number_of_offert - 160) / 25)+1
            element = WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable((By.XPATH, '/html/body/div[6]/button'))
            )
            element.click()
            element = WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable((By.XPATH, '/html/body/div[5]/button'))
            )
            element.click()
            for page in range(number_of_pages):
                try:
                    driver.execute_script("window.scrollBy(0,document.body.scrollHeight)")
                    element = WebDriverWait(driver, 2).until(
                        EC.element_to_be_clickable((By.XPATH, '/html/body/div[3]/div/main/section[2]/button'))
                    )
                    element.click()
                    sleep(2)
                except:
                    continue
            driver.execute_script("window.scrollBy(0,document.body.scrollHeight)")
    # Scrapping full-page
    html = driver.page_source
    driver.close()
    soup = BeautifulSoup(html, "html.parser")
    results = soup.find_all("div", {"class":"base-card relative w-full hover:no-underline focus:no-underline base-card--link base-search-card base-search-card--link job-search-card"})
    # Scrapping detail
    for result in results:
        offert_id = find_digit(result.get("data-entity-urn"))
        link = (result.find("a", {"class":"base-card__full-link"}).get("href")).strip()
        # Checking if offer already exist in database
        offer_exist_in_db = (
            session.query(Linkedin).filter(Linkedin.offert_id == offert_id).count()
        )
        if offer_exist_in_db > 0:
            continue
        else:
            company = (result.find("h4",{"class":"base-search-card__subtitle"}).get_text()).strip()
            title = (result.find("h3", {"class":"base-search-card__title"}).get_text()).strip()
            location = (result.find("span",{"class":"job-search-card__location"}).get_text()).strip()
            try:
                # Calculating delta-date
                time = (result.find("time", {"class":"job-search-card__listdate"}).get_text()).strip()
                days_ago = find_digit(time)
                time = date.today() - timedelta(days=days_ago)
            except:
                time = date.today()

            # Saving details
            new_linked = Linkedin(
                    offert_id = offert_id,
                    time=time,
                    offer_title=title,
                    company_name=company,
                    location=location,
                    wages="NULL",
                    link=link,
                    remote=False,
                )
            new_offer = NewsOffert(
                time=time,
                offer_title=title,
                company_name=company,
                location=location,
                wages="NULL",
                link=link,
                remote=False,
                source="Linkedin",
            )
            session.add_all([new_linked, new_offer])
