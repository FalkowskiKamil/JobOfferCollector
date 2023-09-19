from datetime import datetime
from time import sleep

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from sqlalchemy import and_
from collection_of_website.base_module import BaseSite, NewsOffert, title_checker


class Ziprecruiter(BaseSite):
    __tablename__ = "ZipRecruiter"


def ziprecruiter_function(session):
    # Decrement deadline
    ziprecruiter = Ziprecruiter()
    ziprecruiter.decrement_deadline(session)
    url = "https://www.ziprecruiter.co.uk/jobs/search?l=Remote&q=Junior+Python&remote=full"

    # Init Selenium Driver
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36")
    driver = webdriver.Chrome(options=options)

    headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    results = soup.find_all("li", {"class":"job-listing"})
    number_of_page_ul = soup.find("ul", {"class":"pagination"}).find_all("li")
    number_of_page = len(number_of_page_ul)
    for page in range(2, number_of_page):
        response = requests.get(f'https://www.ziprecruiter.co.uk/jobs/search?l=Remote&page={page}&q=Junior+Python&remote=full', headers=headers)
        soup = BeautifulSoup(response.content, "html.parser")
        results += soup.find_all("li", {"class":"job-listing"})
    
    driver.close()
    for result in results:
        time_raw = result.find("div",{"class":"jobList-date text-muted u-textNoWrap"}).get_text()
        time = datetime.strptime(time_raw + " 2023", "%d %b %Y").date()
        company = result.find("i", {"class":"text-muted fas fa-building"}).next_sibling.get_text()
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
            if title_check == True:
                continue
            keywords = ["account", "german", "french", "customer", "norwegian", "hr", "finnish", "arabic", "armenian", "danish", "kazakh", "romanian", "turkish", "ukrainian", ".net", "java", "italian", "dutch", "php", "helpdesk", 'oracle', 'manager', 'cloud', 'mid', 'mid/senior', 'senior']
            if any(keyword in title.lower() for keyword in keywords):                
                continue
            location = result.find("i", {"class":"text-muted fas fa-map-marker-alt"}).next_sibling.get_text()
            remote = True

            new_ziprecruiter = Ziprecruiter(
                time = time,
                offer_title = title,
                company_name = company,
                location = location,
                link = link,
                remote = remote,)

            new_offer = NewsOffert(
                time = time,
                offer_title = title,
                company_name = company,
                location = location,
                link = link,
                remote = remote,
                source = "Zip Recruiter")
            session.add_all([new_ziprecruiter, new_offer])
