import re
from time import sleep
from datetime import date, timedelta
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By

from base_module import BaseSite, NewsOffert

class Linkedin(BaseSite):
    __tablename__ = "Linkedin"


def linkedin_function(session):
    # Decrement deadline
    linkedin = Linkedin()
    linkedin.decrement_deadline(session)
    
    # Scrapping init
    driver = webdriver.Chrome()
    driver.get(
        "https://www.linkedin.com/jobs/search/?currentJobId=3630027367&f_E=1%2C2&f_TPR=r604800&geoId=90009828&keywords=Python&location=Warszawa%20i%20okolice&refresh=true&sortBy=R"
    )
    sleep(2)

    # Scrolling part
    number_of_offert_text = driver.find_element(By.XPATH, "/html/body/div[3]/div/main/div/h1/span[1]").text
    pattern = r"\d+"
    number_of_offert = int(re.findall(pattern, number_of_offert_text)[0])
    if number_of_offert > 25:
        if number_of_offert < 160:
            scrolling_count = int((number_of_offert / 25)+1)
            for _ in range(scrolling_count):
                driver.execute_script("window.scrollBy(0,document.body.scrollHeight)")
                sleep(2)
        # Button-refreshment part
        number_of_pages = int((number_of_offert - 160) / 25)+1
        for page in range(number_of_pages):
            try:
                driver.execute_script("window.scrollBy(0,document.body.scrollHeight)")
                element = driver.find_element(By.XPATH, "/html/body/div[3]/div/main/section[2]/button")
                sleep(2)
                element.click()
                sleep(2)
            except:
                continue
        driver.execute_script("window.scrollBy(0,document.body.scrollHeight)")
        sleep(2)

    # Scrapping full-page
    html = driver.page_source
    driver.close()
    soup = BeautifulSoup(html, "html.parser")
    results = soup.find_all("div", {"class":"base-card relative w-full hover:no-underline focus:no-underline base-card--link base-search-card base-search-card--link job-search-card"})
    
    # Scrapping detail
    for result in results:
        link = (result.find("a", {"class":"base-card__full-link"}).get("href")).strip()
        company = (result.find("h4",{"class":"base-search-card__subtitle"}).get_text()).strip()
        title = (result.find("h3", {"class":"base-search-card__title"}).get_text()).strip()
        location = (result.find("span",{"class":"job-search-card__location"}).get_text()).strip()
        try:
            # Calculating delta-date
            time = (result.find("time", {"class":"job-search-card__listdate"}).get_text()).strip()
            days_ago = int(re.findall(pattern, time)[0]) 
            time = date.today() - timedelta(days=days_ago)
        except:
            time = date.today()

        # Saving details
        new_linked = Linkedin(
                time=time,
                offer_title=title,
                company_name=company,
                location=location,
                wages="NaN",
                link=link,
                remote=False,
            )
        new_offer = NewsOffert(
            time=time,
            offer_title=title,
            company_name=company,
            location=location,
            wages="Nan",
            link=link,
            remote=False,
            source="Linkedin",
        )
        session.add_all([new_linked, new_offer])
