from bs4 import BeautifulSoup

from collection_of_website.base_module import BaseSite, NewsOffert


class Bulldog(BaseSite):
    __tablename__ = "Bulldog"


def bulldog_function(session, driver):
    # Decrement deadline
    bull_dog = Bulldog()
    bull_dog.decrement_deadline(session)

    # Scrapping data
    driver.get("https://bulldogjob.pl/companies/jobs/s/skills,Python/experienceLevel,junior,intern")
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    results = soup.find_all("a", {"class": "p-3 md:p-5 xs:-mx-6 md:mx-0 flex gap-8 relative bg-white mb-4 md:rounded-lg shadow-jobitem cursor-pointer"})

    # Collecting details
    for result in results:
        link = result.get("href")
        
        # Checking if data already exist in db
        offer_exist_in_db = session.query(Bulldog).filter(Bulldog.link == link).count()
        if offer_exist_in_db > 0: continue
        else:
            title = result.find("h3", {"class": "md:mb-5 lg:mb-0 text-18 font-extrabold leading-8 mr-8 md:mr-0"}).get_text()
            company = result.find("div", {"class": "text-xxs uppercase text-neutral-800 font-semibold tracking-wider"}).get_text()
            places_group = result.find_all("span", {"class": "group flex rounded-md items-center w-full px-2 my-1 font-normal"})
            wages = result.find("div", {"class": "lg:font-extrabold md:text-xl text-dm"}.get_text())
            remote = False
            location = str()

            # Checking remote
            for place in places_group:
                if place.get_text() == "Remote":
                    remote = True
                else:
                    location += place.get_text()

            # Saving data
            new_bulldog_job = Bulldog(
                offer_title=title,
                company_name=company,
                location=location,
                wages=wages,
                link=link,
                remote=remote)
            new_offert = NewsOffert(
                offer_title=title,
                company_name=company,
                location=location,
                wages=wages,
                link=link,
                remote=remote,
                source="Bulldog")
            session.add_all([new_bulldog_job, new_offert])