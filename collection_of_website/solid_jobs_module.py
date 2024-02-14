from bs4 import BeautifulSoup
from time import sleep


from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from collection_of_website.base_module import BaseSite, NewsOffert, create_table, title_checker


class SolidJob(BaseSite):
    __tablename__ = "SolidJobs"


def solid_jobs_function(session, inspector):
    # Creating table if not existing
    if not inspector.has_table(SolidJob.__tablename__):
        session, inspector = create_table(session)

    # Decrement deadline
    solid_jobs = SolidJob()
    solid_jobs.decrement_deadline(session)
    root_link = "https://solid.jobs"
    existing_data = [entry.link for entry in session.query(SolidJob).all()]

    # Init Selenium Driver settings
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36")

    # Scrapping offert
    html_python = "https://solid.jobs/offers/it;experiences=Junior;subcategories=Python"
    results = scrapping_offert(html_python, options)
    html_cyber = "https://solid.jobs/offers/it;cities=Warszawa;categories=Security;experiences=Junior"
    results += scrapping_offert(html_cyber, options)

    # Collecting details
    for result in results:
        link = root_link + result.find("a").get("href")
        # Checking data in db
        if link in existing_data:
            continue
        else:
            # Scrapping details
            title = result.find("h2").get_text().strip()
            title_check = title_checker(title)
            if title_check is True:
                continue

            company = result.find("div", {"class", "flex-row"}).find("a").get_text().strip()
            location = result.find("span", {"class": "mat-tooltip-trigger ng-star-inserted"}).get_text().strip()
            remote = result.find("div", {"class": "d-flex mb-s ng-star-inserted"}).find("a").get_text()
            if remote == " Praca zdalna":
                location += ", Remote"
            # Saving date
            new_solid_job = SolidJob(
                offer_title=title,
                company_name=company,
                location=location,
                link=link,)
            
            new_offer = NewsOffert(
                offer_title=title,
                company_name=company,
                location=location,
                link=link,
                source="solid_job")
            session.add_all([new_solid_job, new_offer])
    return session


def scrapping_offert(html, options):
    driver = webdriver.Chrome(options=options)
    driver.get(html)
    sleep(2)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    results = soup.find_all("offer-list-item")
    driver.close()
    return results
