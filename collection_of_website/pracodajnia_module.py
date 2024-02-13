from datetime import datetime

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from collection_of_website.base_module import BaseSite, NewsOffert, create_table, title_checker


class Pracodajnia(BaseSite):
    __tablename__ = "Pracodajnia"


def pracodajnia_function(session, inspector):
    if not inspector.has_table(Pracodajnia.__tablename__):
        session, inspector = create_table(session)
    # Decrement deadline
    pracodajnia = Pracodajnia()
    pracodajnia.decrement_deadline(session)

    # Init Selenium Driver
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36")
    driver = webdriver.Chrome(options=options)

    # Scrapping data
    driver.get("https://pracodajnia.pl/index.php?list=job&search=python&title=on&description=on")
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    results = soup.find_all("div", {"class": "listing_list mini_rectangle_rounded"})
    root_link = "https:"
    driver.close()

    existing_data = [entry.link for entry in session.query(Pracodajnia).all()]
    # Collecting details
    for result in results:
        link = root_link + result.find("td", {"class": "item ellipsis"}).find("a").get("href")

        # Checking if offer already exist in database
        if link in existing_data:
            continue
        else:            
            time_to_convert = result.find("time").get("datetime").split()[0].strip()
            time = datetime.strptime(time_to_convert, "%Y-%m-%d").date()
            title = result.find("td", {"class": "item ellipsis"}).find("a").get_text().strip().split("\t")[0]
            title_check = title_checker(title)
            if title_check is True:
                continue

            # Saving data
            new_pracodajnia = Pracodajnia(
                time=time,
                offer_title=title,
                link=link)

            new_offer = NewsOffert(
                offer_title=title,
                link=link,
                source="pracodajnia")
            session.add_all([new_pracodajnia, new_offer])
    return session
