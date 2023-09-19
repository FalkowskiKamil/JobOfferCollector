from bs4 import BeautifulSoup
from time import sleep


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from collection_of_website.base_module import BaseSite, NewsOffert


class SolidJob(BaseSite):
    __tablename__ = "SolidJobs"


def solid_jobs_function(session):
    # Decrement deadline
    solid_jobs = SolidJob()
    solid_jobs.decrement_deadline(session)
    
    # Init Selenium Driver
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36")
    driver = webdriver.Chrome(options=options)

    # Scrapping offert
    driver.get("https://solid.jobs/offers/it;experiences=Junior;subcategories=Python")
    sleep(2)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    results = soup.find_all("div", {"class": "card py-2 pl-3 pr-2 mb-2 mr-2 offer left-junior"})
    root_link = "https://solid.jobs"
    driver.close()

    # Collecting details
    for result in results:
        link = root_link + result.find("a", {"class": "color-dark-grey color-blue-onhover"}).get("href")
        # Checking data in db
        offer_exist_in_db = (session.query(SolidJob).filter(SolidJob.link == link).count())
        if offer_exist_in_db > 0: continue
        else:
            # Scrapping details
            title = result.find("a", {"class": "color-dark-grey color-blue-onhover"}).get_text().strip()
            company = result.find("a", {"class": "mat-tooltip-trigger mr-1 color-blue-onhover"}).get_text().strip()
            place = result.find("span", {"class": "mat-tooltip-trigger ng-star-inserted"}).get_text().strip()
            wages = result.find("a", {"class": "mat-tooltip-trigger badge badge-advanced mr-1 d-inline d-md-none no-wrap ng-star-inserted"}).get_text()
            remote = result.find("div",{"class":"d-flex mb-s ng-star-inserted"}).find("a").get_text()
            if remote == " Praca zdalna":
                remote = True
            else:
                remote = False

            # Saving date
            new_solid_job = SolidJob(
                offer_title=title,
                company_name=company,
                location=place,
                wages=wages,
                link=link,
                remote=remote)
            
            new_offer = NewsOffert(
                offer_title=title,
                company_name=company,
                location=place,
                wages=wages,
                link=link,
                remote=remote,
                source="SolidJobs")
            session.add_all([new_solid_job, new_offer])