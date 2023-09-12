from datetime import date, timedelta
from bs4 import BeautifulSoup
from selenium import webdriver

from collection_of_website.base_module import BaseSite, NewsOffert, find_digit


class Infopraca(BaseSite):
    __tablename__ = "Infopraca"


def infopraca_function(session):
    # Decrement deadline
    infopraca = Infopraca()
    infopraca.decrement_deadline(session)


    driver = webdriver.Chrome()
    driver.get("https://www.infopraca.pl/praca?q=python&lc=Warszawa&d=50&pg=1")
    # Scrapping data
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    results = soup.find_all("div",{"class":"job-offer"})
    number_of_offert = find_digit(soup.find("div",{"class":"fs-lg me-4"}).get_text())
    number_of_pages = int(number_of_offert/18)
    for page in range(number_of_pages-1):
            page += 2
            driver.get(f"https://www.infopraca.pl/praca?d=50&lc=&pg={page}&q=python")
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            results += soup.find_all("div",{"class":"job-offer"})
    

    root_link = "https://www.infopraca.pl/"
    for result in results:          
        link = root_link + result.find("h1",{"class":"h3 mb-1"}).find("a").get("href")
        # Checking if offer already exist in database
        offer_exist_in_db = (
            session.query(Infopraca).filter(Infopraca.link == link).count()
        )
        if offer_exist_in_db > 0:
            continue
        else:
            time_raw = result.find("p",{"class":"text-muted small"}).get_text()
            if "Dzisiaj" in time_raw:
                time = date.today()
            elif "wczoraj" in time_raw:
                time = date.today() - timedelta(days=1)
            else:
                # Calculating made of data
                days_ago = find_digit(time_raw)
                time = date.today() - timedelta(days=days_ago)
            title = result.find("a",{"class":"open-job-offer text-secondary"}).get_text()
            company = result.find("h2",{"class":"h5"}).get_text()
            location = result.find_all("p",{"class":"text-muted"})
            if len(location)>3:
                location = location[0].get_text().strip()
            else:
                location = "NULL"
            wages = "NULL"
            remote = False
            
            # Saving details
            new_infopraca = Infopraca(
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
                source="infopraca",
            )
            session.add_all([new_infopraca, new_offer])
    