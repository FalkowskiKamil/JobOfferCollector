from time import sleep
import math
from datetime import date, timedelta
from bs4 import BeautifulSoup
from selenium import webdriver
from sqlalchemy import Column, String
from selenium.webdriver.common.by import By

from collection_of_website.base_module import BaseSite, NewsOffert, find_digit


class Indeed(BaseSite):
    __tablename__ = "Indeed"
    offert_id = Column(String)


def indeed_function(session):
    # Decrement deadline
    indeed = Indeed()
    indeed.decrement_deadline(session)

    driver = webdriver.Chrome()
    driver.get("https://pl.indeed.com/jobs?q=Python&l=Warszawa%2C+mazowieckie&radius=50&fromage=14&vjk=ebe1be7f38146e50")
    sleep(1)
    driver = accept_cookies(driver)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    results = soup.find_all("div",{"class":"job_seen_beacon"})

    number_of_offert_span = soup.find("div",{"class":"jobsearch-JobCountAndSortPane-jobCount css-1af0d6o eu4oa1w0"}).find("span").get_text()

    number_of_offert = find_digit(number_of_offert_span)
    number_of_page = math.ceil(int(number_of_offert) / 15) - 3
    for page in range(number_of_page):
        driver = next_page(driver)
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        results += soup.find_all("div",{"class":"job_seen_beacon"})
    driver.close()

    root_link = "https://indeed.com"
    for result in results:
        id = result.find("a",{"class":"jcs-JobTitle css-jspxzf eu4oa1w0"}).get("id")
        link = root_link + result.find("a",{"class":"jcs-JobTitle css-jspxzf eu4oa1w0"}).get("href")
        
        # Checking if offer already exist in database
        offer_exist_in_db = (
            session.query(Indeed).filter(Indeed.offert_id == id).count()
        )
        if offer_exist_in_db > 0:
            continue
        else:
            try:
                days_ago = find_digit(result.find("span",{"class":"date"}).get_text())
            except:
                if "wczoraj" in result.find("span",{"class":"date"}):
                    days_ago = 1
                else:
                    days_ago = 0
            time = date.today() - timedelta(days=days_ago)
            title = result.find("h2",{"class":"jobTitle"}).find("span").get("title")
            company = result.find("span",{"class":"companyName"}).get_text()
            location = result.find("div",{"class":"companyLocation"}).get_text()
            wages = "NULL"
            remote = False
            if location:
                if "zdal" in location:
                    remote = True

            # Saving details
            new_indeed = Indeed(
                offert_id=id,
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
                source="indeed",
            )
            session.add_all([new_indeed, new_offer])
    




def next_page(driver):
    try:
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        try:
            next_site_button = driver.find_element(By.XPATH, "/html/body/main/div/div[1]/div/div/div[5]/div[1]/nav/div[7]/a")
        except:
            # Case first site
            next_site_button = driver.find_element(By.XPATH, "/html/body/main/div/div[1]/div/div/div[5]/div[1]/nav/div[6]/a")
        sleep(1)
        next_site_button.click()
        return driver
        
    except:
        # Decline login and newsletter
        loggin = driver.find_element(By.XPATH, '//*[@id="google-Only-Modal"]/div/div[1]/button')
        sleep(1)
        loggin.click()
        newsletter = driver.find_element(By.XPATH, '//*[@id="mosaic-desktopserpjapopup"]/div[1]/button')
        sleep(1)
        newsletter.click()
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        try:
            next_site_button = driver.find_element(By.XPATH, "/html/body/main/div/div[1]/div/div/div[5]/div[1]/nav/div[7]/a")
        except:
            next_site_button = driver.find_element(By.XPATH, "/html/body/main/div/div[1]/div/div/div[5]/div[1]/nav/div[6]/a")
        sleep(1)
        next_site_button.click()
        sleep(1)
        return driver

    
def accept_cookies(driver):
    cookie = driver.find_element(By.XPATH, '//*[@id="onetrust-reject-all-handler"]')
    sleep(1)
    cookie.click()
    return driver