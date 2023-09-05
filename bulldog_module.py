from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from sqlalchemy import inspect
from sqlalchemy.orm import sessionmaker

from base_module import BaseSite, NewsOffert, Base, engine


class Bulldog(BaseSite):
    __tablename__ = "Bulldog"


def bulldog_function():
    inspector = inspect(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    driver = webdriver.Chrome()
    driver.get(
        "https://bulldogjob.pl/companies/jobs/s/skills,Python/experienceLevel,junior,intern"
    )
    sleep(1)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    # Checking table exists
    if not inspector.has_table(NewsOffert.__tablename__):
        Base.metadata.create_all(engine)
    if not inspector.has_table(Bulldog.__tablename__):
        Base.metadata.create_all(engine)
    else:
        bull_dog = Bulldog()
        bull_dog.decrement_deadline(session)
        print("decrement deadline by 1 day")

    results = soup.find_all(
        "div",
        {
            "class": "p-3 md:p-5 xs:-mx-6 md:mx-0 flex gap-8 relative bg-white mb-4 md:rounded-lg shadow-jobitem cursor-pointer"
        },
    )
    for result in results:
        link = result.find_parent("a").get("href")
        offer_exist_in_db = session.query(Bulldog).filter(Bulldog.link == link).count()
        if offer_exist_in_db > 0:
            continue
        else:
            title = result.find(
                "h3", {"class": "text-18 font-extrabold leading-8 mr-8 md:mr-0"}
            ).get_text()
            company = result.find(
                "div",
                {
                    "class": "text-xxs uppercase text-neutral-800 font-semibold tracking-wider"
                },
            ).get_text()
            places_group = result.find_all(
                "span",
                {
                    "class": "group flex rounded-md items-center w-full px-2 my-1 font-normal"
                },
            )
            remote = False
            place_list = str()
            for place in places_group:
                if place.get_text() == "Remote":
                    remote = True
                else:
                    place_list += place.get_text()
            new_bulldog_job = Bulldog(
                offer_title=title,
                company_name=company,
                location=place_list,
                link=link,
                remote=remote,
            )
            session.add(new_bulldog_job)
            new_offert = NewsOffert(
                offer_title=title,
                company_name=company,
                location=place_list,
                link=link,
                remote=remote,
                source="Bulldog",
            )
            session.add(new_offert)
            session.commit()
    session.close()
