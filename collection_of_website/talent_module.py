import requests
from bs4 import BeautifulSoup

from collection_of_website.base_module import BaseSite, NewsOffert


class Talent(BaseSite):
    __tablename__ = "Talent"



def talent_function(session):
    # Decrement deadline
    talent = Talent()
    talent.decrement_deadline(session)    
    
    # Scrapping data
    html = requests.get("https://pl.talent.com/pl/jobs?k=Python&l=Warsaw%2C+Mazovia&radius=50")
    soup = BeautifulSoup(html.content, "html.parser")
    results = soup.find_all("div",{"class":"link-job-wrap"})

    root_site = "https://pl.talent.com/view?id="
    # Iterating over offert
    for result in results:
        link = root_site + result.find_parent("div",{"class":"card"}).get("data-id")
        # Checking if offer already exist in database
        offer_exist_in_db = (
            session.query(Talent).filter(Talent.link == link).count()
        )
        if offer_exist_in_db > 0:
            continue
        else:
            title = result.get("title")
            company = result.find("div",{"class":"card__job-empname-label"}).get_text()
            location = result.find("div",{"class":"card__job-location"}).get_text()
            try:
                wages = result.find("div",{"class":"card__job-badge-wrap card__job-badge-salary"}).get_text()
            except:
                wages = "NULL"
            remote = False
            # Saving details
            new_talent = Talent(
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
                source="Talent",
            )
            session.add_all([new_talent, new_offer])