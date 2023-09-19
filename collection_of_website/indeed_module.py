import math
from datetime import date, timedelta

from bs4 import BeautifulSoup
from sqlalchemy import Column, String
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from collection_of_website.base_module import BaseSite, NewsOffert, find_digit, title_checker


class Indeed(BaseSite):
    __tablename__ = "Indeed"
    offert_id = Column(String)


def indeed_function(session):
    # Decrement deadline
    indeed = Indeed()
    indeed.decrement_deadline(session)

    # Init Selenium Driver
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36")
    driver = webdriver.Chrome(options=options)

    # Scrapping offert
    driver.get("https://pl.indeed.com/jobs?q=Python&l=Warszawa%2C+mazowieckie&radius=50&fromage=14&vjk=ebe1be7f38146e50")
    cookie = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="onetrust-reject-all-handler"]')))
    cookie.click()
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    results = soup.find_all("div", {"class":"job_seen_beacon"})
    root_link = "https://indeed.com"

    # Iterating over pages
    number_of_offert_span = soup.find("div", {"class":"jobsearch-JobCountAndSortPane-jobCount css-1af0d6o eu4oa1w0"}).find("span").get_text()
    number_of_offert = find_digit(number_of_offert_span)
    number_of_page = math.ceil(int(number_of_offert) / 15) - 4
    for page in range(number_of_page):
        driver = next_page(driver)
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        results += soup.find_all("div", {"class":"job_seen_beacon"})

    driver.close()
    # Collecting details
    for result in results:
        id = result.find("a", {"class":"jcs-JobTitle css-jspxzf eu4oa1w0"}).get("id")
        
        # Checking if offer already exist in database
        offer_exist_in_db = (session.query(Indeed).filter(Indeed.offert_id == id).count())
        if offer_exist_in_db > 0: continue
        else:
            # Transform date
            try:
                days_ago = find_digit(result.find("span", {"class":"date"}).get_text())
            except:
                if "wczoraj" in result.find("span", {"class":"date"}):
                    days_ago = 1
                else:
                    days_ago = 0
            time = date.today() - timedelta(days=days_ago)
            link = root_link + result.find("a", {"class":"jcs-JobTitle css-jspxzf eu4oa1w0"}).get("href")
            title = result.find("h2", {"class":"jobTitle"}).find("span").get("title")
            title_check = title_checker(title)
            if title_check == True:
                continue
            company = result.find("span", {"class":"companyName"}).get_text()
            location = result.find("div", {"class":"companyLocation"}).get_text()
            wages = None
            remote = False
            if location:
                if "zdal" in location:
                    remote = True
            # Saving data
            new_indeed = Indeed(
                offert_id=id,
                time=time,
                offer_title=title,
                company_name=company,
                location=location,
                wages=wages,
                link=link,
                remote=remote)

            new_offer = NewsOffert(
                time=time,
                offer_title=title,
                company_name=company,
                location=location,
                wages=wages,
                link=link,
                remote=remote,
                source="Indeed")
            session.add_all([new_indeed, new_offer])

def next_page(driver):
    try:
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        try:
            next_site_button = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.XPATH, "/html/body/main/div/div/div[1]/div/div/div[5]/div[1]/nav/div[7]/a")))
        except:
            # Case for first & last site        
            next_site_button = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.XPATH, "/html/body/main/div/div/div[1]/div/div/div[5]/div[1]/nav/div[6]/a")))
        next_site_button.click()
        return driver
        
    except:
        # Decline login and newsletter
        
        loggin = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[3]/div[1]/div[1]/button')))
        loggin.click()
        newsletter = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="close"]')))
        newsletter.click()
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        try:
            next_site_button = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.XPATH, "/html/body/main/div/div/div[1]/div/div/div[5]/div[1]/nav/div[7]/a")))        
        except:
            # Case for first & last site           
            next_site_button = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.XPATH, "/html/body/main/div/div/div[1]/div/div/div[5]/div[1]/nav/div[6]/a")))
        next_site_button.click()
        return driver