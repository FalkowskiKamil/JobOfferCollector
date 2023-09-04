import requests
from time import strftime, sleep
from datetime import date
from bs4 import BeautifulSoup
import sqlite3
from selenium import webdriver
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Date
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import inspect  # Dodajemy import

db_path = "jobs_creator.db"  # Ścieżka do bazy danych
engine = create_engine(f"sqlite:///{db_path}")
Base = declarative_base()


class BaseSite(Base):
    __abstract__ = True  # Ustalamy klasę jako abstrakcyjną
    id = Column(Integer, primary_key=True)
    time = Column(Date)
    offer_title = Column(String)
    company_name = Column(String)
    location = Column(String)
    link = Column(String, unique=True)
    remote = Column(Boolean)
    applicated = Column(Boolean)

# Teraz możesz dziedziczyć z BaseJob dla każdej konkretnej tabeli
class SolidJob(BaseSite):
    __tablename__ = 'solid_jobs'

class AnotherJob(BaseSite):
    __tablename__ = 'another_jobs'

def solid_jobs():
    driver = webdriver.Chrome()
    driver.get("https://solid.jobs/offers/it;experiences=Junior;subcategories=Python")
    sleep(1)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    results = soup.find_all("div", {"class":"card py-2 pl-3 pr-2 mb-2 mr-2 offer left-junior"})
    root_link = "https://solid.jobs"
    # Checking table exists
    inspector = inspect(engine)
    if not inspector.has_table(SolidJob.__tablename__):
        Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()   
    for result in results:     
        link = result.find("a", {"class":"color-dark-grey color-blue-onhover"}).get("href")
        link = root_link + link
        offer_exist_in_db = session.query(SolidJob).filter(SolidJob.link == link).count()        
        if offer_exist_in_db > 0:
            print("Oferta już istnieje w bazie danych")
            continue
        else:
            time = date.today()
            title = result.find("a", {"class":"color-dark-grey color-blue-onhover"}).get_text()
            company = result.find("a", {"class":"mat-tooltip-trigger mr-1 color-blue-onhover"}).get_text()
            place = result.find("span", {"class":"mat-tooltip-trigger ng-star-inserted"}).get_text()
            remote = result.find("a", {"class":"mat-tooltip-trigger badge badge-extra hoverable mr-1", "mattooltip":"Możliwa praca hybrydowa. Kliknij, aby zobaczyć inne oferty pracy hybrydowej."}).get_text()
            if remote == " Praca zdalna":
                remote = True
            else:
                remote = False
            applicated = False
            new_job = SolidJob(time=time, offer_title=title, company_name=company, location=place,
                            link=link, remote=remote, applicated=applicated)
            session.add(new_job)
            session.commit()
    session.close()

solid_jobs()

def bulldog():
    link = requests.get("https://bulldogjob.pl/companies/jobs/s/skills,Python/experienceLevel,junior,intern")
    soup = BeautifulSoup(link.content, "html.parser")
    results = soup.find_all("div",{"class":"p-3 md:p-5 xs:-mx-6 md:mx-0 flex gap-8 relative bg-white mb-4 md:rounded-lg shadow-jobitem cursor-pointer"})
    for result in results:
        time = strftime("%d-%m %H:%M")
        title = result.find("h3", {"class":"text-18 font-extrabold leading-8 mr-8 md:mr-0"}).get_text()
        company = result.find("div", {"class":"text-xxs uppercase text-neutral-800 font-semibold tracking-wider"}).get_text()
        places_group = result.find_all("span",{"class":"group flex rounded-md items-center w-full px-2 my-1 font-normal"})
        remote = False
        place_list = []
        for place in places_group:
            if place.get_text() == "Remote":
                remote = True
            else:
                place_list.append(place.get_text())
        print(remote)
        print(*place_list, sep=", ")
        print(title)
        print(company)
        applicated = False
        

#bulldog()