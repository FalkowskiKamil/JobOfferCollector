from datetime import date

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from collection_of_website.base_module import BaseSite, NewsOffert, create_table, date_translate, find_digit, title_checker


class Olx(BaseSite):
    __tablename__ = "OLX"


def olx_function(session, inspector):
    if not inspector.has_table(Olx.__tablename__):
        session, inspector = create_table(session)

    # Decrement deadline
    olx = Olx()
    olx.decrement_deadline(session)

    # Init Selenium Driver
    options = Options()
    options.add_argument('--headless=new')
    # options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36")
    driver = webdriver.Chrome(options=options)
    # Scrapping init
    driver.get("https://www.olx.pl/praca/q-Python/?page=1")
    try:
        cookie_button = WebDriverWait(driver, 3).until(ec.element_to_be_clickable((By.XPATH, '//*[@id="onetrust-accept-btn-handler"]')))
    except:
        cookie_button = None
    if cookie_button:
        cookie_button.click()
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    root_site = "https://www.olx.pl"
    
    # Checking count of offert
    results = soup.find_all("a", {"class": "css-rc5s2u"})
    number_of_offert_text = soup.find("span", {"data-testid": "total-count"}).get_text()
    number_of_offert = find_digit(number_of_offert_text)

    # Calculating next-page count offert
    if number_of_offert > 40:
        number_of_pages_ul = soup.find("ul", {"class": "pagination-list"})
        number_of_pages_raw = list(number_of_pages_ul.find_all("li"))[-1].get_text()
        number_of_pages = int(number_of_pages_raw.strip()) - 1
        # Collecting data from next pages
        for page in range(2, number_of_pages+2):
            try:
                driver.get(f"https://www.olx.pl/praca/q-Python/?page={page}")
            except:
                cookie_button = WebDriverWait(driver, 3).until(ec.element_to_be_clickable((By.XPATH, '//*[@id="onetrust-accept-btn-handler"]')))
                if cookie_button:
                    cookie_button.click()
                driver.get(f"https://www.olx.pl/praca/q-Python/?page={page}")
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            results += soup.find_all("a", {"class": "css-rc5s2u"})
    driver.close()

    existing_data = [entry.link for entry in session.query(Olx).all()]
    # Collecting details
    for result in results:
        link = root_site + result.get("href")

        # Checking if data already in db
        if link in existing_data: 
            continue
        else:
            existing_data.append(link)
            try:
                time_tag = result.find("div", {"class": "css-g39uhb"}).find("p")
                # Clearing date data
                if "Dzisiaj" in time_tag.get_text():
                    time = date.today()
                elif "Odświeżono" in time_tag.get_text():
                    time = date_translate(time_tag.get_text().removeprefix("Odświeżono dnia "))
                elif "Dodane" in time_tag.get_text():
                    time = date_translate(time_tag.get_text().removeprefix("Dodane "))
                else:
                    time = date_translate(time_tag.get_text())
                title = result.find("h6", {"class": "css-1jmx98l"}).get_text()
                title_check = title_checker(title)
                if title_check is True:
                    continue
                company = None
                location = result.find("span", {"class": "css-d5w927"}).get_text()
                
                # Searching of remote-avaibility
                additional_info = result.find_all("span", {"class": "css-1m53r4k"})
                for info in additional_info:
                    if info.get_text() == "Praca zdalna dozwolona":
                        location += ", Remote"
                        break

                # Saving data
                new_olx = Olx(
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
                    source="olx")
                session.add_all([new_olx, new_offer]) 
            except:
                continue
    return session
