from datetime import datetime
import requests
from bs4 import BeautifulSoup

from collection_of_website.base_module import BaseSite, NewsOffert


class JobsPl(BaseSite):
    __tablename__ = "JobsPl"


def jobspl_function(session):
    # Decrement deadline
    jobspl = JobsPl()
    #jobspl.decrement_deadline(session)

    # Scrapping data
    html = requests.get("https://www.jobs.pl/oferty/python;k")
    soup = BeautifulSoup(html.content, "html.parser")
    results = soup.find_all("div",{"class":"offer-border offer"})
    root_link = "https://www.jobs.pl/"
    for result in results:
        link = root_link + result.find("div",{"class":"offer-title"}).find("a").get("href")
        # Checking if offer already exist in database
        offer_exist_in_db = (
            session.query(JobsPl).filter(JobsPl.link == link).count()
        )
        if offer_exist_in_db > 0:
            continue
        else:
            title = result.find("div",{"class":"offer-title"}).find("a").get_text().strip()
            company = result.find("p",{"class":"offer-employer"}).find("a").get_text()
            time_to_convert = result.find("p",{"class":"offer-date"}).get_text().strip()
            time = datetime.strptime(time_to_convert, '%d.%m.%Y').date()
            location = result.find("p",{"class":"offer-location"}).find("a").get_text()
            remote = False
            wages = "NaN"
            # Saving details
            new_jobspl = JobsPl(
                time=time,
                offer_title=title,
                company_name=company,
                location=location,
                wages=wages,
                link=link,
                remote=remote,
            )

            new_offer = NewsOffert(
                time=time,
                offer_title=title,
                company_name=company,
                location=location,
                wages=wages,
                link=link,
                remote=remote,
                source="Jobspl",
            )
            session.add_all([new_jobspl, new_offer])