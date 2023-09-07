import re
from time import sleep
from datetime import date, timedelta
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from sqlalchemy import inspect
from sqlalchemy.orm import sessionmaker

from base_module import BaseSite, NewsOffert, Base, engine


class Linkedin(BaseSite):
    __tablename__ = "Linkedin"


def linkedin_function():
    # Connect to Database
    inspector = inspect(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Checking if table exists
    if not inspector.has_table(Linkedin.__tablename__):
        Base.metadata.create_all(engine)
    else:
        # Decrement deadline
        linkedin = Linkedin()
        linkedin.decrement_deadline(session)
    
    # Scrapping init
    driver = webdriver.Chrome()
    driver.get(
        "https://www.linkedin.com/jobs/search/?currentJobId=3630027367&f_E=1%2C2&f_TPR=r604800&geoId=90009828&keywords=Python&location=Warszawa%20i%20okolice&refresh=true&sortBy=R"
    )
    sleep(2)

    # Scrolling Section
    number_of_offert_text = driver.find_element(By.XPATH, "/html/body/div[3]/div/main/div/h1/span[1]").text
    pattern = r"\d+"
    number_of_offert = int(re.findall(pattern, number_of_offert_text)[0])
    if number_of_offert > 25:
        for x in range(7):
            driver.execute_script("window.scrollBy(0,document.body.scrollHeight)")
            sleep(2)

    # Button-refreshment section
    if number_of_offert > 160:
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

    # Scrapping next-page
    html = driver.page_source
    driver.close()
    soup = BeautifulSoup(html, "html.parser")
    total_offert = soup.find_all("div", {"class":"base-card relative w-full hover:no-underline focus:no-underline base-card--link base-search-card base-search-card--link job-search-card"})
    
    # Scrapping detail
    for result in total_offert:
        link = result.find("a", {"class":"base-card__full-link"}).get("href")
        link = link.strip()
        company = result.find("h4",{"class":"base-search-card__subtitle"}).get_text()
        company = company.strip()
        title = result.find("h3", {"class":"base-search-card__title"}).get_text()
        title = title.strip()
        location = result.find("span",{"class":"job-search-card__location"}).get_text()
        location = location.strip()
        try:
            # Calculating delta-date
            offert_date = result.find("time", {"class":"job-search-card__listdate"}).get_text()
            offert_date = offert_date.strip()
            days_ago = int(re.findall(pattern, offert_date)[0]) 
            offert_date = date.today() - timedelta(days=days_ago)
        except:
            offert_date = date.today()

        # Saving details
        new_linked = Linkedin(
                time=offert_date,
                offer_title=title,
                company_name=company,
                location=location,
                wages="NaN",
                link=link,
                remote=False,
            )
        new_offer = NewsOffert(
            time=offert_date,
            offer_title=title,
            company_name=company,
            location=location,
            wages="Nan",
            link=link,
            remote=False,
            source="Linkedin",
        )
        session.add_all([new_linked, new_offer])
    session.commit()
    session.close()
