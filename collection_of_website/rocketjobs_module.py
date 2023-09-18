import requests
from bs4 import BeautifulSoup

from collection_of_website.base_module import BaseSite, NewsOffert

class Rocketjobs(BaseSite):
    __tablename__ = "RocketJobs"


def rocketjobs_function(session):
    # Decrement deadline
    rocketjobs = Rocketjobs()
    rocketjobs.decrement_deadline(session)

    # Scrapping offert
    html = requests.get("https://rocketjobs.pl/warszawa/doswiadczenie_staz-junior?keyword=Python")
    soup = BeautifulSoup(html.content, "html.parser")
    results = soup.find_all("div", {"class":"css-6xbxgh"})
    root_link = "https://rocketjobs.pl"

    # Collecting details
    for result in results:
        link = root_link + result.find("a").get("href")

        # Checking if offer already exist in database
        offer_exist_in_db = (session.query(Rocketjobs).filter(Rocketjobs.link == link).count())
        if offer_exist_in_db > 0: continue
        else:
            title = result.find("h2").get_text()
            company = result.find("div", {"class":"css-jx23jo"}).find("span").get_text()
            location = result.find("div", {"class":"css-1wao8p8"}).get_text()
            try:
                wages = result.find("div", {"class":"css-lz8wxo"}).find_all("span")
                wages = wages[0].get_text() + " - " + wages[1].get_text() + " " + wages[2].get_text()
            except:
                wages = None
            remote = result.find("div", {"class":"css-12973y2"}).get_text() == "Zdalnie"

            # Saving details
            new_rocket = Rocketjobs(
                offer_title=title,
                company_name=company,
                location=location,
                wages=wages,
                link=link,
                remote=remote,
            )

            new_offer = NewsOffert(
                offer_title=title,
                company_name=company,
                location=location,
                wages=wages,
                link=link,
                remote=remote,
                source="RocketJobs",
            )
            session.add_all([new_rocket, new_offer])