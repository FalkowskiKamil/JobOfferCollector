import os

from sqlalchemy import inspect, func
from sqlalchemy.orm import sessionmaker
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from collection_of_website.adzuna_module import adzuna_function
from collection_of_website.bulldog_module import bulldog_function
from collection_of_website.glassdor_module import glassdor_function
from collection_of_website.indeed_module import indeed_function
from collection_of_website.infopraca_module import infopraca_function
from collection_of_website.jobspl_module import jobspl_function
from collection_of_website.just_join_module import just_join_function
from collection_of_website.linkedin_module import linkedin_function
from collection_of_website.nofluffjobs_module import nofluffjobs_function
from collection_of_website.olx_module import olx_function
from collection_of_website.pracodajnia_module import pracodajnia_function
from collection_of_website.pracuj_module import pracuj_function
from collection_of_website.rocketjobs_module import rocketjobs_function
from collection_of_website.solid_jobs_module import solid_jobs_function
from collection_of_website.szukampracy_module import szukampracy_function
from collection_of_website.talent_module import talent_function
from collection_of_website.theprotocol_module import theprotocol_function
from collection_of_website.base_module import Base, engine, BaseSite, NewsOffert

def collect_offert(args=None):

    # Init session
    inspector = inspect(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Checking db
    if not inspector.has_table(NewsOffert.__tablename__):
        Base.metadata.create_all(engine)

    elif args == "last":
        source_counts = (
            session.query(NewsOffert.source, func.count(NewsOffert.source)).group_by(NewsOffert.source).all())
        for source, count in source_counts:
            print(f"{count}x{source}")
        return
    elif args == "init":
        Base.metadata.create_all(engine)
    else:
        # Deleting last searching data
        session.query(NewsOffert).delete()
        # Deleting data oldest than 30 days
        for table_class in BaseSite.__subclasses__():
            records_to_delete = (session.query(table_class).filter(table_class.days_until_deadline == 0).all())
            for record in records_to_delete:
                session.delete(record)
        session.commit()
        
    # Init selenium sesion
    options = Options()
    options.add_argument('--headless=new')
    driver = webdriver.Chrome(options=options)

    #Scraping over sites
    linkedin_function(session, driver) # Unordered linkedin to avoid tracking
    adzuna_function(session)
    bulldog_function(session, driver)
    glassdor_function(session, driver)
    indeed_function(session, driver)
    infopraca_function(session, driver)
    jobspl_function(session)
    just_join_function(session, driver)
    nofluffjobs_function(session)
    olx_function(session, driver)
    pracodajnia_function(session, driver)
    pracuj_function(session, driver)
    rocketjobs_function(session)
    solid_jobs_function(session, driver)
    szukampracy_function(session)
    talent_function(session)
    theprotocol_function(session)
    driver.close()

    # Saving results
    session.commit()
    session.close()

    # Clearing terminal
    clear = lambda: os.system("cls" if os.name == "nt" else "clear")
    clear()

    # Summary of scrapping
    source_counts = (session.query(NewsOffert.source, func.count(NewsOffert.source)).group_by(NewsOffert.source).all())
    for source, count in source_counts:
        print(f"{count}x{source}")