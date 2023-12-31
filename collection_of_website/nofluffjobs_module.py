import requests
from bs4 import BeautifulSoup

from collection_of_website.base_module import BaseSite, NewsOffert, title_checker


class Nofluffjobs(BaseSite):
    __tablename__ = "NoFluffJobs"


def nofluffjobs_function(session):
    # Decrement deadline
    nofluffjobs = Nofluffjobs()
    nofluffjobs.decrement_deadline(session)

    # Scrapping data
    html = requests.get("https://nofluffjobs.com/pl/praca-zdalna/Python?page=1&criteria=city%3Dwarszawa%20%20seniority%3Dtrainee,junior")
    soup = BeautifulSoup(html.content, "html.parser")
    container_div = soup.find("div", {"class": "list-container ng-star-inserted"})
    results = container_div.find_all("a", {"class": "posting-list-item"})
    root_site = "https://nofluffjobs.com"

    # Calculating number of site
    number_of_site_ul = soup.find("ul", {"class": "pagination mb-0 ng-star-inserted"})
    number_of_site = number_of_site_ul.find_all("li")
    number_of_site = int(list(number_of_site)[-2].get_text().strip()) - 1

    # Iterating over sites
    for site in range(2, number_of_site + 2):
        html = requests.get(f"https://nofluffjobs.com/pl/praca-zdalna/Python?page={site}&criteria=city%3Dwarszawa%20%20seniority%3Dtrainee,junior")
        soup = BeautifulSoup(html.content, "html.parser")
        container_div = soup.find("div", {"class": "list-container ng-star-inserted"})
        results += container_div.find_all("a", {"class": "posting-list-item"})
        
    # Collecting detils
    for result in results:
        link = result.get("href")
        link = root_site + link

        # Checking if offer already exist in database
        offer_exist_in_db = (session.query(Nofluffjobs).filter(Nofluffjobs.link == link).count())
        if offer_exist_in_db > 0: continue
        else:
            # Scrapping details
            title = result.find("h3").get_text()
            title_check = title_checker(title)
            if title_check == True:
                continue
            company = result.find("span").get_text().strip()
            location = result.find("span", {"class": "tw-text-ellipsis tw-inline-block tw-overflow-hidden tw-whitespace-nowrap lg:tw-max-w-[100px] tw-text-right"}).get_text()
            wages = result.find("span", {"class": "text-truncate badgy salary tw-btn tw-btn-secondary-outline tw-btn-xs ng-star-inserted"}).get_text()
            remote = False
            if location == " Zdalnie ":
                remote = True

            # Saving data
            new_nofluffjobs = Nofluffjobs(
                offer_title=title,
                company_name=company,
                location=location,
                wages=wages,
                link=link,
                remote=remote,)

            new_offer = NewsOffert(
                offer_title=title,
                company_name=company,
                location=location,
                wages=wages,
                link=link,
                remote=remote,
                source="NoFluffJobs")
            session.add_all([new_nofluffjobs, new_offer])