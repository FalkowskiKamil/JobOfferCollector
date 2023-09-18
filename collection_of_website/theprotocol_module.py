import requests
from bs4 import BeautifulSoup

from collection_of_website.base_module import BaseSite, NewsOffert


class Theprotocol(BaseSite):
    __tablename__ = "Theprotocol"


def theprotocol_function(session):
    # Decrement deadline
    theprotocol = Theprotocol()
    theprotocol.decrement_deadline(session) 

    # Scrapping details   
    html = requests.get("https://theprotocol.it/filtry/python;t/trainee,assistant,junior;p/warszawa;wp")
    soup = BeautifulSoup(html.content, "html.parser")
    box_results = soup.find("div",{"class":"o1onjy6t"})
    results = box_results.find_all("a", {"class":"anchorClass_a6of9et"})
    root_site = "https://theprotocol.it"

    # Collecting details
    for result in results:
        link = root_site + result.get("href")

        # Checking if offer already exist in database
        offer_exist_in_db = (session.query(Theprotocol).filter(Theprotocol.link == link).count())
        if offer_exist_in_db > 0: continue
        else:
            title = result.find("h2").get_text()
            company = result.find("div", {"class":"rootClass_rpqnjlt body1_b1gato5c initial_i1m6fsnc textClass_t1rna8so"}).get_text()
            location = result.find_all("div", {"class":"rootClass_rpqnjlt body1_b1gato5c initial_i1m6fsnc textClass_t1rna8so"})[-1].get_text()
            try: 
                wages = result.find("span", {"class":"boldText_b1wsb650"}).get_text()
            except:
                wages = None
            remote = result.find_all("div", {"class":"rootClass_rpqnjlt body1_b1gato5c initial_i1m6fsnc textClass_t1rna8so"})[-2].get_text()
            if remote == "zdalna":
                remote = True
            else:
                remote = False
            
            # Saving date
            new_theprotocol = Theprotocol(
                offer_title=title,
                company_name=company,
                location=location,
                wages=wages,
                link=link,
                remote=remote)

            new_offer = NewsOffert(
                offer_title=title,
                company_name=company,
                location=location,
                wages=wages,
                link=link,
                remote=remote,
                source="Theprotocol")
            session.add_all([new_theprotocol, new_offer])