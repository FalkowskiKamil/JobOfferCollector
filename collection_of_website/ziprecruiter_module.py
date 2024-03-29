from datetime import datetime

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from sqlalchemy import and_
from collection_of_website.base_module import BaseSite, NewsOffert, create_table, title_checker


class Ziprecruiter(BaseSite):
    __tablename__ = "ZipRecruiter"


def ziprecruiter_function(session, inspector):
    # Creating table if not existing
    if not inspector.has_table(Ziprecruiter.__tablename__):
        session, inspector = create_table(session)
    # Decrement deadline
    ziprecruiter = Ziprecruiter()
    ziprecruiter.decrement_deadline(session)

    # Init Selenium Driver setting
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36")

    # Scrapping offert
    html_python = "https://www.ziprecruiter.co.uk/jobs/search?l=Remote&q=Junior+Python&remote=full"
    results = scrapping_offert(html_python, options)

    for result in results:
        time_raw = result.find("div", {"class": "jobList-date text-muted u-textNoWrap"}).get_text()
        time = datetime.strptime(time_raw + " 2023", "%d %b %Y").date()
        company = result.find("i", {"class": "text-muted fas fa-building"}).next_sibling.get_text()
        # Checking if offert already exist in database
        offer_exist_in_db = (
            session.query(Ziprecruiter).filter(and_(Ziprecruiter.time == time, Ziprecruiter.company_name == company)).count()
        )
        if offer_exist_in_db > 0:
            continue
        else:
            link = result.find("a").get("href")
            title = result.find("a").get_text()
            title_check = title_checker(title)
            if title_check is True:
                continue
            location = result.find("i", {"class": "text-muted fas fa-map-marker-alt"}).next_sibling.get_text() + ", Remote"

            new_ziprecruiter = Ziprecruiter(
                time=time,
                offer_title=title,
                company_name=company,
                location=location,
                link=link,)

            new_offer = NewsOffert(
                offer_title=title,
                company_name=company,
                location=location,
                link=link,
                source="ziprecruiter")
            session.add_all([new_ziprecruiter, new_offer])
    return session


def scrapping_offert(html, options):
    driver = webdriver.Chrome(options=options)
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
    response = requests.get(html, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    results = soup.find_all("li", {"class": "job-listing"})
    number_of_page_ul = soup.find("ul", {"class": "pagination"}).find_all("li")
    number_of_page = len(number_of_page_ul)
    for page in range(2, number_of_page):
        response = requests.get(f'https://www.ziprecruiter.co.uk/jobs/search?l=Remote&page={page}&q=Junior+Python&remote=full', headers=headers)
        soup = BeautifulSoup(response.content, "html.parser")
        results += soup.find_all("li", {"class": "job-listing"})
    driver.close()
    return results
