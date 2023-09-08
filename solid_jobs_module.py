from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from sqlalchemy import inspect
from sqlalchemy.orm import sessionmaker

from base_module import BaseSite, NewsOffert, Base, engine


class SolidJob(BaseSite):
    __tablename__ = "Solid_Jobs"


def solid_jobs_function():
    # Connect to Database
    inspector = inspect(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Checking if table exists
    if not inspector.has_table(SolidJob.__tablename__):
        Base.metadata.create_all(engine)
    else:
        # Decrement deadline
        solid_jobs = SolidJob()
        solid_jobs.decrement_deadline(session)
    
    # Init scrapping
    driver = webdriver.Chrome()
    driver.get("https://solid.jobs/offers/it;experiences=Junior;subcategories=Python")
    sleep(1)
    html = driver.page_source
    driver.close()
    soup = BeautifulSoup(html, "html.parser")
    results = soup.find_all(
        "div", {"class": "card py-2 pl-3 pr-2 mb-2 mr-2 offer left-junior"}
    )
    root_link = "https://solid.jobs"

    # Iterating over offert
    for result in results:
        link = root_link + result.find("a", {"class": "color-dark-grey color-blue-onhover"}).get(
            "href"
        )
        # Checking data in db
        offer_exist_in_db = (
            session.query(SolidJob).filter(SolidJob.link == link).count()
        )
        if offer_exist_in_db > 0:
            continue
        else:
            # Scrapping details
            title = (
                result.find("a", {"class": "color-dark-grey color-blue-onhover"})
                .get_text()
                .lstrip()
            )
            company = (
                result.find(
                    "a", {"class": "mat-tooltip-trigger mr-1 color-blue-onhover"}
                )
                .get_text()
                .lstrip()
            )
            place = (
                result.find("span", {"class": "mat-tooltip-trigger ng-star-inserted"})
                .get_text()
                .lstrip()
            )
            wages = result.find(
                "a",
                {
                    "class": "mat-tooltip-trigger badge badge-advanced mr-1 d-inline d-md-none no-wrap ng-star-inserted"
                },
            ).get_text()
            remote = result.find(
                "a",
                {
                    "class": "mat-tooltip-trigger badge badge-extra hoverable mr-1",
                    "mattooltip": "Możliwa praca hybrydowa. Kliknij, aby zobaczyć inne oferty pracy hybrydowej.",
                },
            ).get_text()
            if remote == " Praca zdalna":
                remote = True
            else:
                remote = False
            # Saving details
            new_solid_job = SolidJob(
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
                source="Solid Jobs",
            )
            session.add_all([new_solid_job, new_offer])
    session.commit()
    session.close()
