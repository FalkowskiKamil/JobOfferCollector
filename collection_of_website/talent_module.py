
import requests
from bs4 import BeautifulSoup

from collection_of_website.base_module import BaseSite, NewsOffert, create_table,  title_checker


class Talent(BaseSite):
    __tablename__ = "Talent"


def talent_function(session, inspector):
    # Creating table if not existing
    if not inspector.has_table(Talent.__tablename__):
        session, inspector = create_table(session)

    # Decrement deadline
    talent = Talent()
    talent.decrement_deadline(session)    
    root_site = "https://pl.talent.com/view?id="
    existing_data = [entry.link for entry in session.query(Talent).all()]

    # Scrapping data
    html_python = "https://pl.talent.com/pl/jobs?k=Python&l=Warsaw%2C+Mazovia&radius=50"
    results = scrapping_offert(html_python)

    html_cyber = "https://pl.talent.com/pl/jobs?k=junior+Security&l=Warsaw%2C+Mazovia&radius=50"
    results += scrapping_offert(html_cyber)

    # Collecting details
    for result in results:
        link = root_site + result.find_parent("div", {"class": "card"}).get("data-id")

        # Checking if offer already exist in database
        if link in existing_data:
            continue
        else:
            title = result.get("title")
            title_check = title_checker(title)
            if title_check is True:
                continue
            company = result.find("div", {"class": "card__job-empname-label"}).get_text()
            location = result.find("div", {"class": "card__job-location"}).get_text()

            # Saving details
            new_talent = Talent(
                offer_title=title,
                company_name=company,
                location=location,
                link=link)

            new_offer = NewsOffert(
                offer_title=title,
                company_name=company,
                location=location,
                link=link,
                source="talent")
            session.add_all([new_talent, new_offer])
    return session


def scrapping_offert(html):
    html = requests.get(html)
    soup = BeautifulSoup(html.content, "html.parser")
    results = soup.find_all("div", {"class": "link-job-wrap"})
    return results
