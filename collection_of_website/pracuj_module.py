
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from collection_of_website.base_module import BaseSite, NewsOffert, date_translate, find_digit, title_checker


class Pracuj(BaseSite):
    __tablename__ = "Pracuj.pl"


def pracuj_function(session):
    # Decrement deadline
    pracuj = Pracuj()
    pracuj.decrement_deadline(session)
    # Init Selenium Driver
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36")
    driver = webdriver.Chrome(options=options)
    # Scrapping init
    driver.get("https://www.pracuj.pl/praca/python;kw/warszawa;wp?rd=30&cc=5016001%2C5016002%2C5016003%2C5016004%2C5001%2C5002%2C5003%2C5004%2C5005%2C5006%2C5037%2C5036%2C5007%2C5008%2C5009%2C5010%2C5011%2C5015%2C5014%2C5013%2C5012%2C5035%2C5033%2C5032%2C5031%2C5028%2C5027%2C5025%2C5026%2C5024%2C5023%2C5022%2C5021%2C5020%2C5019%2C5018%2C5017%2C5034&et=1%2C17&pn=1")
    cookie_button = WebDriverWait(driver, 4).until(ec.element_to_be_clickable((By.CSS_SELECTOR, "button[data-test='button-submitCookie']")))
    cookie_button.click()
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    # Searching of offert and page count
    try:
        page_number_text = soup.find("div", {"class": "listing_w1sj4gb8"}).get_text()
        page_number = find_digit(page_number_text) - 1

    except:
        page_number = 0
    section_offers = soup.find("div", {"data-test": "section-offers"})
    results = section_offers.find_all("div", {"data-test": "default-offer"})
    # Iterating over pages

    if page_number > 0:
        for page in range(1, page_number + 1):
            driver.get(f"https://www.pracuj.pl/praca/python;kw/warszawa;wp?rd=30&cc=5016001%2C5016002%2C5016003%2C5016004%2C5001%2C5002%2C5003%2C5004%2C5005%2C5006%2C5037%2C5036%2C5007%2C5008%2C5009%2C5010%2C5011%2C5015%2C5014%2C5013%2C5012%2C5035%2C5033%2C5032%2C5031%2C5028%2C5027%2C5025%2C5026%2C5024%2C5023%2C5022%2C5021%2C5020%2C5019%2C5018%2C5017%2C5034&et=1%2C17&pn={page}")
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            section_offers = soup.find("div", {"data-test": "section-offers"})
            results += section_offers.find_all("div", {"data-test": "default-offer"})
    driver.close()
    existing_data = [entry.link for entry in session.query(Pracuj).all()]

    # Collecting details
    for result in results:
        try:
            link = (result.find("a")).get("href")
            if "%s" in link or "?s" in link:
                link = link.split("?s")[0]
            # Checking if data already in db
            if link in existing_data:
                continue
            else:
                existing_data.append(link)
                # Tranform date
                time_tag = result.find("p").get_text()
                time = date_translate(time_tag.removeprefix("Opublikowana: "))
                title = result.find("h2").get_text()
                title_check = title_checker(title)
                if title_check is True:
                    continue
                company = result.find("a", {"data-test": "link-company-profile"}).get_text()
                try:
                    location = result.find("h5", {"data-test": "text-region"}).get_text()
                except:
                    location = result.find("strong").get_text()
                # Saving data
                new_pracuj = Pracuj(
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
                    source="pracuj")
                session.add_all([new_pracuj, new_offer])
        except:
            continue
