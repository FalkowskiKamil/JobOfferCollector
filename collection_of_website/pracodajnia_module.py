from datetime import datetime

from bs4 import BeautifulSoup

from collection_of_website.base_module import BaseSite, NewsOffert


class Pracodajnia(BaseSite):
    __tablename__ = "Pracodajnia"


def pracodajnia_function(session, driver):
    # Decrement deadline
    pracodajnia = Pracodajnia()
    pracodajnia.decrement_deadline(session)

    # Scrapping data
    driver.get("https://pracodajnia.pl/index.php?list=job&search=python&title=on&description=on")
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    results = soup.find_all("div", {"class":"listing_list mini_rectangle_rounded"})
    root_link = "https:"

    # Collecting details
    for result in results:
        link = root_link + result.find("td", {"class":"item ellipsis"}).find("a").get("href")

        # Checking if offer already exist in database
        offer_exist_in_db = (session.query(Pracodajnia).filter(Pracodajnia.link == link).count())
        if offer_exist_in_db > 0: continue
        else:            
            time_to_convert = result.find("time").get("datetime").split()[0].strip()
            time = datetime.strptime(time_to_convert, "%Y-%m-%d").date()
            title = result.find("td", {"class":"item ellipsis"}).find("a").get_text().strip().split("\t")[0]
            wages = result.find("span", {"style":"float:right"}).get_text()

            # Saving data
            new_pracodajnia = Pracodajnia(
                time=time,
                offer_title=title,
                wages=wages,
                link=link)

            new_offer = NewsOffert(
                time=time,
                offer_title=title,
                wages=wages,
                link=link,
                source="Pracodajnia")
            session.add_all([new_pracodajnia, new_offer])
