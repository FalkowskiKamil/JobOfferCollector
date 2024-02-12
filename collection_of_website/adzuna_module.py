import requests
from bs4 import BeautifulSoup

from collection_of_website.base_module import BaseSite, NewsOffert, title_checker


class Adzuna(BaseSite):
    __tablename__ = "Adzuna"

def adzuna_module_function(session):
    # Decrement deadline
    adzuna = Adzuna()
    adzuna.decrement_deadline(session)

    # Scrapping offert
    html = "https://www.adzuna.pl/search?adv=1&d=50&f=7&loc=129972&pp=50&sb=date&sd=down&qtl=Junior&qwd=Python"
    response = requests.get(html)
    soup = BeautifulSoup(response.content, "html.parser")
    results = soup.find_all("div", {"class": "a flex gap-2 md:gap-4 p-3 md:pb-1 border-b border-solid border-adzuna-gray-200 cursor-pointer hover:bg-adzuna-green-100 hover:border-adzuna-green-100 md:border md:rounded-lg md:mb-4"})

    existing_data = [entry.link for entry in session.query(Adzuna).all()]

    # Collecting details
    for result in results:
        link = result.find("a", {"class": "text-base md:text-xl lg:text-2xl text-adzuna-green-500 hover:underline"}).get("href")

        # Integrate offert
        if "?se=" in link:
            link = link.split("?se=")[0]
        if "/land/ad/" in link:
            continue
        # Checking if offer already exist in database
        if link in existing_data:
            continue
        else:
            title = result.find("a", {"class": "text-base md:text-xl lg:text-2xl text-adzuna-green-500 hover:underline"}).get_text().strip()
            title_check = title_checker(title)
            if title_check is True:
                continue
            company = result.find("div", {"class": "ui-company"})
            if company:
                company = company.get_text()
            location = result.find("div", {"ui-location text-adzuna-gray-900"}).get_text()
            try:
                remote_box = result.find("div", {"class": "flex flex-wrap gap-1 my-1"})
                remote = remote_box.find("span", {"class": "inline-block text-xs bold rounded leading-none p-1 border border-blue-600 bg-blue-600 text-white"}).get_text() == "PRACA ZDALNA"
                if remote:
                    location += ", Remote"
            except:
                pass
            # Saving data
            new_adzuna = Adzuna(
                offer_title=title,
                company_name=company,
                location=location,
                link=link,)

            new_offer = NewsOffert(
                offer_title=title,
                company_name=company,
                location=location,
                link=link,
                source="adzuna")
            session.add_all([new_adzuna, new_offer])
