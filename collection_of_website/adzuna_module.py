import math
from bs4 import BeautifulSoup
import requests

from collection_of_website.base_module import BaseSite, NewsOffert, find_digit


class Adzuna(BaseSite):
    __tablename__ = "Adzuna"


def adzuna_function(session):
    # Decrement deadline
    adzuna = Adzuna()
    adzuna.decrement_deadline(session)

    html = "https://www.adzuna.pl/search?adv=1&loc=129972&pp=50&qtl=Junior&qwd=Python"

    # Response1
    response = requests.get(html)
    soup = BeautifulSoup(response.content, "html.parser")
    results = soup.find_all("div",{"class":"a flex gap-2 md:gap-4 p-3 md:pb-1 border-b border-solid border-adzuna-gray-200 cursor-pointer hover:bg-adzuna-green-100 hover:border-adzuna-green-100 md:border md:rounded-lg md:mb-4"})

    number_of_offert = int(soup.find("h1").find("span").get("data-cy-count"))
    number_of_page = math.ceil(number_of_offert/50)
    for page in range(number_of_page):
        page +=2
        response = requests.get(f'https://www.adzuna.pl/search?adv=1&loc=129972&pp=50&qtl=Junior&qwd=Python&page={page}')
        soup = BeautifulSoup(response.content, "html.parser")
        results += soup.find_all("div",{"class":"a flex gap-2 md:gap-4 p-3 md:pb-1 border-b border-solid border-adzuna-gray-200 cursor-pointer hover:bg-adzuna-green-100 hover:border-adzuna-green-100 md:border md:rounded-lg md:mb-4"})

    for result in results:
        link = result.find("a",{"class":"text-base md:text-xl lg:text-2xl text-adzuna-green-500 hover:underline"}).get("href")
        if "?se=" in link:
            link = link.split("?se=")[0]
        # Checking if offer already exist in database
        offer_exist_in_db = (
            session.query(Adzuna).filter(Adzuna.link == link).count()
        )
        if offer_exist_in_db > 0:
            continue
        else:
            title = result.find("a",{"class":"text-base md:text-xl lg:text-2xl text-adzuna-green-500 hover:underline"}).get_text().strip()
            try:
                company = result.find("div",{"class":"ui-company"}).get_text()
            except:
                company = 'NULL'
            location = result.find("div",{"ui-location text-adzuna-gray-900"}).get_text()
            wages = result.find("div",{"class":"ui-salary flex flex-wrap gap-x-2"})
            if wages:
                try:
                    wages = find_digit(wages.get_text().strip())
                except:
                    wages = "NULL"
            else:
                wages = "NULL"
            remote = result.find("div",{"class":"flex flex-wrap gap-1 my-1"})
            if remote:
                try:
                    remote = remote.find("span",{"class":"inline-block text-xs bold rounded leading-none p-1 border border-blue-600 bg-blue-600 text-white"}).get_text() == "PRACA ZDALNA"
                except:
                    remote = False
            else:
                remote = False
        
            # Saving details
            new_adzuna = Adzuna(
                offer_title=title,
                company_name=company,
                location=location,
                wages=wages,
                link=link,
                remote=remote,
            )

            new_offer = NewsOffert(
                offer_title=title,
                company_name=company,
                location=location,
                wages=wages,
                link=link,
                remote=remote,
                source="adzuna",
            )
            session.add_all([new_adzuna, new_offer])
    