import math
from datetime import date, timedelta

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from collection_of_website.base_module import BaseSite, NewsOffert, create_table,  find_digit, title_checker


class Infopraca(BaseSite):
    __tablename__ = "Infopraca"


def infopraca_function(session, inspector):
    # Creating table if not existing
    if not inspector.has_table(Infopraca.__tablename__):
        session, inspector = create_table(session)

    # Decrement deadline
    infopraca = Infopraca()
    infopraca.decrement_deadline(session)
    existing_data = [entry.link for entry in session.query(Infopraca).all()]
    root_link = "https://www.infopraca.pl/"

    # Init Selenium Driver setting
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36")

    # Scrapping Python & SOC offert
    html_python = "https://www.infopraca.pl/praca?d=50&lc=Warszawa&q=python"
    results = scrapping_offert(html_python, options)
    html_security = "https://www.infopraca.pl/praca?d=50&lc=Warszawa&q=security"
    results += scrapping_offert(html_security, options)

    # Collecting details
    for result in results:          
        link = root_link + result.find("h1", {"class": "h3 mb-1"}).find("a").get("href")
        
        # Checking if offer already exist in database
        if link in existing_data:
            continue
        else:
            # Transform date
            time_raw = result.find("p", {"class": "text-muted small"}).get_text()
            if "Dzisiaj" in time_raw:
                time = date.today()
            elif "wczoraj" in time_raw:
                time = date.today() - timedelta(days=1)
            else:
                days_ago = find_digit(time_raw)
                time = date.today() - timedelta(days=days_ago)
            title = result.find("a", {"class": "open-job-offer text-secondary"}).get_text()
            title_check = title_checker(title)
            if title_check is True:
                continue
            company = result.find("h2", {"class": "h5"}).get_text()
            location = result.find_all("p", {"class": "text-muted"})
            if len(location) > 3:
                location = location[0].get_text().strip()
            else:
                location = None

            # Saving data
            new_infopraca = Infopraca(
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
                source="infopraca")
            session.add_all([new_infopraca, new_offer])
    return session


def scrapping_offert(html, options):
    driver = webdriver.Chrome(options=options)
    driver.get(html)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    results = soup.find_all("div", {"class": "job-offer"})

    # Iterating over pages
    number_of_offert = find_digit(soup.find("div", {"class": "fs-lg me-4"}).get_text())
    number_of_pages = math.ceil(number_of_offert/18) - 1
    for page in range(2, number_of_pages + 2):
        driver.get(f"{html}&pg={page}")
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        results += soup.find_all("div", {"class": "job-offer"})
    driver.close()
    return results
