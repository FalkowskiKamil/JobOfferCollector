import math
from datetime import date, timedelta

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from collection_of_website.base_module import BaseSite, NewsOffert, find_digit, title_checker


class Infopraca(BaseSite):
    __tablename__ = "Infopraca"


def infopraca_function(session):
    # Decrement deadline
    infopraca = Infopraca()
    infopraca.decrement_deadline(session)

    # Init Selenium Driver
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36")
    driver = webdriver.Chrome(options=options)

    # Scrapping data
    driver.get("https://www.infopraca.pl/praca?q=python&lc=Warszawa&d=50&pg=1")
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    results = soup.find_all("div",{"class":"job-offer"})
    root_link = "https://www.infopraca.pl/"

    # Iterating over pages
    number_of_offert = find_digit(soup.find("div",{"class":"fs-lg me-4"}).get_text())
    number_of_pages = math.ceil(number_of_offert/18) - 1
    for page in range(2, number_of_pages +2):
        driver.get(f"https://www.infopraca.pl/praca?d=50&lc=&pg={page}&q=python")
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        results += soup.find_all("div",{"class":"job-offer"})
    driver.close()
    
    # Collecting details
    for result in results:          
        link = root_link + result.find("h1",{"class":"h3 mb-1"}).find("a").get("href")
        
        # Checking if offer already exist in database
        offer_exist_in_db = (session.query(Infopraca).filter(Infopraca.link == link).count())
        if offer_exist_in_db > 0: continue
        else:
            # Transform date
            time_raw = result.find("p",{"class":"text-muted small"}).get_text()
            if "Dzisiaj" in time_raw:
                time = date.today()
            elif "wczoraj" in time_raw:
                time = date.today() - timedelta(days=1)
            else:
                days_ago = find_digit(time_raw)
                time = date.today() - timedelta(days=days_ago)
            title = result.find("a",{"class":"open-job-offer text-secondary"}).get_text()
            title_check = title_checker(title)
            if title_check == True:
                continue
            company = result.find("h2",{"class":"h5"}).get_text()
            location = result.find_all("p",{"class":"text-muted"})
            if len(location)>3:
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
                time=time,
                offer_title=title,
                company_name=company,
                location=location,
                link=link,
                source="Infopraca")
            session.add_all([new_infopraca, new_offer])
    