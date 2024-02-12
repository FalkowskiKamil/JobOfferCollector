from datetime import date, timedelta

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from collection_of_website.base_module import BaseSite, NewsOffert, find_digit, title_checker


class JustJoin(BaseSite):
    __tablename__ = "Just Join"


def just_join_function(session):
    # Decrement deadline
    just_join = JustJoin()
    just_join.decrement_deadline(session)

    # Init Selenium Driver
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36")
    driver = webdriver.Chrome(options=options)

    # Scrapping data
    driver.get("https://justjoin.it/warszawa/python/experience-level_junior")
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")    
    results = soup.find_all("div", {"item": "[object Object]"})
    root_site = "https://justjoin.it"

    driver.close()
    link_list = [str(entry.link) for entry in session.query(JustJoin).all()]
    # Collecting details
    if len(results) == 0:
        raise ValueError
    for result in results:
        link = root_site + result.find("a", {"class": "css-4lqp8g"})["href"]
        if str(link) in link_list:
            continue
        else:
            link_list.append(link)
            # Transform date
            time = result.find("div", {"class": "css-1am4i4o"}).get_text()
            if time == "New":
                time = date.today()
            else:
                days_ago = find_digit(time)
                time = date.today() - timedelta(days=days_ago)
            title = result.find("img").get("alt")
            
            title_check = title_checker(title)
            if title_check is True:
                continue
            company = result.find("span").get_text()
            location = result.find("span", {"class": "css-1o4wo1x"}).get_text()
            if "Fully Remote" in location:
                location += ", Remote"
            # Saving data
            new_just_join = JustJoin(
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
                source="just_join")
            session.add_all([new_just_join, new_offer])
