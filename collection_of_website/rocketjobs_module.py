
import requests
from bs4 import BeautifulSoup

from collection_of_website.base_module import BaseSite, NewsOffert, create_table, title_checker


class Rocketjobs(BaseSite):
    __tablename__ = "RocketJobs"


def rocketjobs_function(session, inspector):
    if not inspector.has_table(Rocketjobs.__tablename__):
        session, inspector = create_table(session)
    # Decrement deadline
    rocketjobs = Rocketjobs()
    rocketjobs.decrement_deadline(session)

    # Scrapping offert
    html = requests.get("https://rocketjobs.pl/warszawa/doswiadczenie_staz-junior?keyword=Python")
    soup = BeautifulSoup(html.content, "html.parser")
    results = soup.find_all("div", {"class": "css-6xbxgh"})
    root_link = "https://rocketjobs.pl"

    existing_data = [entry.link for entry in session.query(Rocketjobs).all()]
    # Collecting details
    for result in results:
        link = root_link + result.find("a").get("href")

        # Checking if offer already exist in database
        if link in existing_data:
            continue
        else:
            title = result.find("h2").get_text()
            title_check = title_checker(title)
            if title_check is True:
                continue
            company = result.find("div", {"class": "css-jx23jo"}).find("span").get_text()
            location = result.find("div", {"class": "css-1wao8p8"}).get_text()
            remote = result.find("div", {"class": "css-12973y2"}).get_text() == "Zdalnie"
            if remote:
                location += ", Remote"

            # Saving details
            new_rocket = Rocketjobs(
                offer_title=title,
                company_name=company,
                location=location,
                link=link,
            )

            new_offer = NewsOffert(
                offer_title=title,
                company_name=company,
                location=location,
                link=link,
                source="rocket",
            )
            session.add_all([new_rocket, new_offer])
    return session
