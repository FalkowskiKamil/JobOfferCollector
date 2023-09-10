import requests
from bs4 import BeautifulSoup

from collection_of_website.base_module import BaseSite, NewsOffert


class Szukampracy(BaseSite):
    __tablename__ = "SzukamPracy"


def szukampracy_function(session):
    # Decrement deadline
    szukampracy = Szukampracy()
    szukampracy.decrement_deadline(session)

    # Scrapping data
    html = requests.get("https://szukampracy.pl/ogloszenie/strona/1?SearchForm%5Bstanowisko%5D=Python&SearchForm%5Bregion%5D%5B0%5D=3&SearchForm%5Bkategorie%5D=")
    soup = BeautifulSoup(html.content, "html.parser")
    ul_list = soup.find_all("ul",{"class":"offer-list"})
    results = ul_list[1].find_all("li",{"class":"ad-on-list"})
    number_of_pages_container = soup.find("ul",{"class":"pagination"})
    number_of_pages = len(number_of_pages_container.find_all("li"))-2
    for page in range(number_of_pages):
        page +=2
        html = requests.get(f"https://szukampracy.pl/ogloszenie/strona/{page}?SearchForm%5Bstanowisko%5D=Python&SearchForm%5Bregion%5D%5B0%5D=3&SearchForm%5Bkategorie%5D=")
        soup = BeautifulSoup(html.content, "html.parser")
        ul_list = soup.find_all("ul",{"class":"offer-list"})
        results += ul_list[0].find_all("li",{"class":"ad-on-list"})
        break

    root_link = "https://szukampracy.pl"
    for result in results:          
        link = root_link + box.find("a").get("href")
        # Checking if offer already exist in database
        offer_exist_in_db = (
            session.query(Szukampracy).filter(Szukampracy.link == link).count()
        )
        if offer_exist_in_db > 0:
            continue
        else:
            company = result.find("a").get("title")
            box = result.find("span",{"class":"description nun-sb"})
            title = box.find("h3").get_text()
            time = box.find("span",{"class":"nun-b"}).get_text()
            location = box.find("a", {"class":"nun-b"}).get_text().strip().split()[0]
            wages = "NaN"
            remote = False
            
            # Saving details
            new_szukam_pracy = Szukampracy(
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
                source="SzukamPracy",
            )
            session.add_all([new_szukam_pracy, new_offer])

