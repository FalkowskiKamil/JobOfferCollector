import requests
from bs4 import BeautifulSoup

from collection_of_website.base_module import BaseSite, NewsOffert, create_table, title_checker


class Nofluffjobs(BaseSite):
    __tablename__ = "NoFluffJobs"


def nofluffjobs_function(session, inspector):
    # Creating table if not existing
    if not inspector.has_table(Nofluffjobs.__tablename__):
        session, inspector = create_table(session)

    # Decrement deadline
    nofluffjobs = Nofluffjobs()
    nofluffjobs.decrement_deadline(session)
    root_site = "https://nofluffjobs.com"

    # Scrapping data
    html_python = "https://nofluffjobs.com/pl/praca-zdalna/Python?page=1&criteria=city%3Dwarszawa%20%20seniority%3Dtrainee,junior"
    results = scrapping_offert(html_python)
    html_cyber = "https://nofluffjobs.com/pl/praca-zdalna/security?page=1&criteria=city%3Dwarszawa%20%20seniority%3Dtrainee,junior"
    results += scrapping_offert(html_cyber)

    existing_data = [entry.link for entry in session.query(Nofluffjobs).all()]
    # Collecting detils
    for result in results:
        link = result.get("href")
        link = root_site + link

        # Checking if offer already exist in database
        if link in existing_data: 
            continue
        else:
            existing_data.append(link)
            # Scrapping details
            title = result.find("h3").get_text().strip()
            title_check = title_checker(title)
            if title_check is True:
                continue
            location = result.find("nfj-posting-item-city")
            company = result.find("h4").get_text().strip()
            location = location.get_text().strip().split(" ")[0]
            # Saving data
            new_nofluffjobs = Nofluffjobs(
                offer_title=title,
                company_name=company,
                location=location,
                link=link,)

            new_offer = NewsOffert(
                offer_title=title,
                company_name=company,
                location=location,
                link=link,
                source="nofluffjobs")
            session.add_all([new_nofluffjobs, new_offer])
    return session


def scrapping_offert(html):
    html = requests.get(html)
    soup = BeautifulSoup(html.content, "html.parser")
    div_container = soup.find("div", {"class": "list-container ng-star-inserted"})
    results = div_container.find_all("a", {"class": "posting-list-item"})
    if len(results) > 19:
        html = requests.get(f"https://nofluffjobs.com/pl/praca-zdalna/Python?page=2&criteria=city%3Dwarszawa%20%20seniority%3Dtrainee,junior")
        soup = BeautifulSoup(html.content, "html.parser")
        div_container = soup.find("div", {"class": "list-container ng-star-inserted"})
        results_new_page = div_container.find_all("a", {"class": "posting-list-item"})
        results += results_new_page
    return results
