from datetime import datetime

import requests
from bs4 import BeautifulSoup

from collection_of_website.base_module import BaseSite, NewsOffert, create_table, title_checker


class Szukampracy(BaseSite):
    __tablename__ = "SzukamPracy"


def szukampracy_function(session, inspector):
    # Creating table if not existing
    if not inspector.has_table(Szukampracy.__tablename__):
        session, inspector = create_table(session)

    # Decrement deadline
    szukampracy = Szukampracy()
    szukampracy.decrement_deadline(session)
    existing_data = [entry.link for entry in session.query(Szukampracy).all()]
    root_link = "https://szukampracy.pl"

    html_python = "https://szukampracy.pl/ogloszenie/strona/1?SearchForm%5Bstanowisko%5D=Python&SearchForm%5Bregion%5D%5B0%5D=3&SearchForm%5Bkategorie%5D="
    results = scrapping_offert(html_python)
    html_cyber = "https://szukampracy.pl/ogloszenie/strona/1?SearchForm%5Bstanowisko%5D=Security&SearchForm%5Bregion%5D%5B0%5D=3&SearchForm%5Bkategorie%5D="
    results += scrapping_offert(html_cyber)

    # Collecting details
    for result in results:   
        box = result.find("span", {"class": "description nun-sb"})
        link = root_link + box.find("a").get("href")
        # Checking if offer already exist in database
        if link in existing_data:
            continue
        else:
            company = result.find("a").get("title")
            title = box.find("h3").get_text()
            title_check = title_checker(title)
            if title_check is True:
                continue
            time_raw = box.find("span", {"class": "nun-b"}).get_text()
            time = datetime.strptime(time_raw, '%d-%m-%Y')
            location = box.find("a", {"class": "nun-b"}).get_text().strip().split()[0]
            # Saving details
            new_szukam_pracy = Szukampracy(
                time=time,
                offer_title=title,
                company_name=company,
                location=location,
                link=link)

            new_offer = NewsOffert(
                offer_title=title,
                company_name=company,
                location=location,
                link=link,
                source="szukam_pracy")
            session.add_all([new_szukam_pracy, new_offer])
    return session


def scrapping_offert(html):
    html = requests.get(html)
    soup = BeautifulSoup(html.content, "html.parser")
    ul_list = soup.find("ul", {"class": "offer-list"})
    results = ul_list.find_all("li", {"class": "ad-on-list"})
    # Iterating over pages
    try:
        number_of_pages_container = soup.find("ul", {"class": "pagination"})
    except:
        number_of_pages_container = None
    if number_of_pages_container:
        number_of_pages = len(number_of_pages_container.find_all("li"))-2
        for page in range(2, number_of_pages+2):
            html = requests.get(f"https://szukampracy.pl/ogloszenie/strona/{page}?SearchForm%5Bstanowisko%5D=Python&SearchForm%5Bregion%5D%5B0%5D=3&SearchForm%5Bkategorie%5D=")
            soup = BeautifulSoup(html.content, "html.parser")
            ul_list = soup.find_all("ul", {"class": "offer-list"})
            results += ul_list[0].find_all("li", {"class": "ad-on-list"})
    return results
