from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from collection_of_website.base_module import BaseSite, NewsOffert, create_table, title_checker


class Bulldog(BaseSite):
    __tablename__ = "Bulldog"


def bulldog_function(session, inspector):
    # Creating table if not existing
    if not inspector.has_table(Bulldog.__tablename__):
        session, inspector = create_table(session)

    # Decrement deadline
    bull_dog = Bulldog()
    bull_dog.decrement_deadline(session)
    existing_data = [entry.link for entry in session.query(Bulldog).all()]

    # Init Selenium Driver setting
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36")

    # Scrapping python offert
    results = scrapping_data(html="https://bulldogjob.pl/companies/jobs/s/skills,Python/experienceLevel,junior,intern", options=options)

    # Scrapping CyberSecurity offert
    results += scrapping_data(html="https://bulldogjob.pl/companies/jobs/s/experienceLevel,junior,intern/role,security", options=options)

    # Collecting details
    for result in results:
        link = result.get("href")
        # Checking if data already exist in db
        if link in existing_data:
            continue
        else:
            title = result.find("h3").get_text()
            title_check = title_checker(title)
            if title_check is True:
                continue
            company = result.find("div", {"class": "text-xxs uppercase text-neutral-800 font-semibold tracking-wider"}).get_text()
            places_group = result.find_all("span", {"class": "group flex rounded-md items-center w-full px-2 my-1 font-normal"})
            location = str()
            # Checking remote
            for place in places_group:
                if place.get_text() == "Remote":
                    location += ", Remote"
                else:
                    location += place.get_text()
            # Saving data
            new_bulldog_job = Bulldog(
                offer_title=title,
                company_name=company,
                location=location,
                link=link)
            
            new_offert = NewsOffert(
                offer_title=title,
                company_name=company,
                location=location,
                link=link,
                source="bulldog")
            session.add_all([new_bulldog_job, new_offert])
    return session


def scrapping_data(html, options):
    driver = webdriver.Chrome(options=options)
    driver.get(html)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    container = soup.find_all("div", {"class": "container"})
    results = container[1].find_all("a")
    driver.close()
    return results
