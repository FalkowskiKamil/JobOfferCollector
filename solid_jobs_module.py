from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from sqlalchemy import inspect 
from sqlalchemy.orm import sessionmaker

from base_module import BaseSite, Base, engine


class SolidJob(BaseSite):
    __tablename__ = 'Solid_Jobs'


def solid_jobs_function():
    driver = webdriver.Chrome()
    driver.get("https://solid.jobs/offers/it;experiences=Junior;subcategories=Python")
    sleep(1)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    results = soup.find_all("div", {"class":"card py-2 pl-3 pr-2 mb-2 mr-2 offer left-junior"})
    root_link = "https://solid.jobs"
    inspector = inspect(engine)
    Session = sessionmaker(bind=engine)
    session = Session() 
    
    # Checking table exists
    if not inspector.has_table(SolidJob.__tablename__):
        Base.metadata.create_all(engine)
    else:
        solid_jobs = SolidJob()
        solid_jobs.decrement_deadline(session)
        print("decrement deadline by 1 day")
    
    for result in results:     
        link = result.find("a", {"class":"color-dark-grey color-blue-onhover"}).get("href")
        link = root_link + link
        offer_exist_in_db = session.query(SolidJob).filter(SolidJob.link == link).count()        
        if offer_exist_in_db > 0:
            continue
        else:
            title = result.find("a", {"class":"color-dark-grey color-blue-onhover"}).get_text()
            company = result.find("a", {"class":"mat-tooltip-trigger mr-1 color-blue-onhover"}).get_text()
            place = result.find("span", {"class":"mat-tooltip-trigger ng-star-inserted"}).get_text()
            remote = result.find("a", {"class":"mat-tooltip-trigger badge badge-extra hoverable mr-1", "mattooltip":"Możliwa praca hybrydowa. Kliknij, aby zobaczyć inne oferty pracy hybrydowej."}).get_text()
            if remote == " Praca zdalna":
                remote = True
            else:
                remote = False
            new_job = SolidJob(offer_title=title, company_name=company, location=place,
                            link=link, remote=remote)
            session.add(new_job)
            session.commit()
    session.close()