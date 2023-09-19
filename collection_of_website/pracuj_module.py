from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from collection_of_website.base_module import BaseSite, NewsOffert, date_translate, find_digit


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
    cookie_button = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div[4]/div/div/div/div[3]/div/button[1]")))
    cookie_button.click()
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    # Searching of offert and page count
    page_number_text = soup.find("div", {"class": "listing_w1sj4gb8"}).get_text()
    page_number = find_digit(page_number_text) - 1
    section_offers = soup.find("div", {"data-test": "section-offers"})
    results = section_offers.find_all("div", {"class": "listing_b1evff58 listing_po9665q"})

    # Iterating over pages
    for page in range(1, page_number + 1):
        driver.get(f"https://www.pracuj.pl/praca/python;kw/warszawa;wp?rd=30&cc=5016001%2C5016002%2C5016003%2C5016004%2C5001%2C5002%2C5003%2C5004%2C5005%2C5006%2C5037%2C5036%2C5007%2C5008%2C5009%2C5010%2C5011%2C5015%2C5014%2C5013%2C5012%2C5035%2C5033%2C5032%2C5031%2C5028%2C5027%2C5025%2C5026%2C5024%2C5023%2C5022%2C5021%2C5020%2C5019%2C5018%2C5017%2C5034&et=1%2C17&pn={page}")
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        section_offers = soup.find("div", {"data-test": "section-offers"})
        results += section_offers.find_all("div", {"class": "listing_b1evff58 listing_po9665q"})
    driver.close()

    # Collecting details
    for result in results:
        try:
            link = (result.find("a", {"class": "listing_o1dyw02w"})).get("href")
            if "%s" in link or "?s" in link:
                link = link.split("?s")[0]

            # Checking if data already in db
            offer_exist_in_db = (session.query(Pracuj).filter(Pracuj.link == link).count())
            if offer_exist_in_db > 0: continue
            else:
                # Tranform date
                time_tag = result.find("p",{"class": "listing_b1nrtp6c listing_pk4iags size-caption listing_t1rst47b"}).get_text()
                time = date_translate(time_tag.removeprefix("Opublikowana: "))
                title = result.find("a", {"class": "listing_o1dyw02w listing_n194fgoq"}).get_text()
                company = result.find("h4", {"class": "listing_eiims5z size-caption listing_t1rst47b"}).get_text()
                try:
                    location = result.find("h5", {"class": "listing_rdl5oe8 size-caption listing_t1rst47b"}).get_text()
                except:
                    location = result.find("strong").get_text()
                try:
                    wages = result.find("span", {"class": "listing_sug0jpb"}).get_text()
                except:
                    wages = None
                remote = False
                additional_information = result.find_all("li", {"class": "listing_isg28kc"})
                for information in additional_information:
                    if information.get_text() == "Praca zdalna":
                        remote = True
                        break

                # Saving data
                new_pracuj = Pracuj(
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
                    source="Pracuj.pl")
                session.add_all([new_pracuj, new_offer])
        except:
            continue