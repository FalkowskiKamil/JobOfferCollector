import requests
from bs4 import BeautifulSoup

from collection_of_website.base_module import BaseSite, NewsOffert, create_table, title_checker


class Theprotocol(BaseSite):
    __tablename__ = "Theprotocol"


def theprotocol_function(session, inspector):
    if not inspector.has_table(Theprotocol.__tablename__):
        session, inspector = create_table(session)

    # Decrement deadline
    theprotocol = Theprotocol()
    theprotocol.decrement_deadline(session) 

    # Scrapping details   
    html = requests.get("https://theprotocol.it/filtry/python;t/trainee,assistant,junior;p/warszawa;wp")
    soup = BeautifulSoup(html.content, "html.parser")
    results = soup.find_all("a", {"data-test": "list-item-offer"})
    root_site = "https://theprotocol.it"

    existing_data = [entry.link for entry in session.query(Theprotocol).all()]
    # Collecting details
    for result in results:
        link = root_site + result.get("href")

        # Checking if offer already exist in database
        if link in existing_data:
            continue
        else:
            title = result.find("h2").get_text()
            title_check = title_checker(title)
            if title_check is True:
                continue
            company = result.find("div", {"class": "rootClass_rpqnjlt body1_b1gato5c initial_i1m6fsnc textClass_t1rna8so"}).get_text()
            location = result.find_all("div", {"class": "rootClass_rpqnjlt body1_b1gato5c initial_i1m6fsnc textClass_t1rna8so"})[-1].get_text()
            remote = result.find_all("div", {"class": "rootClass_rpqnjlt body1_b1gato5c initial_i1m6fsnc textClass_t1rna8so"})[-2].get_text()
            if remote == "zdalna":
                location += ", Remote"
            
            # Saving date
            new_theprotocol = Theprotocol(
                offer_title=title,
                company_name=company,
                location=location,
                link=link,)

            new_offer = NewsOffert(
                offer_title=title,
                company_name=company,
                location=location,
                link=link,
                source="theprotocol")
            session.add_all([new_theprotocol, new_offer])
    return session
