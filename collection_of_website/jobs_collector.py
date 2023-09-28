import os
import inspect
from time import sleep
import traceback
import winsound

from sqlalchemy import inspect, func
from sqlalchemy.orm import sessionmaker

from collection_of_website.adzuna_module import adzuna_function
from collection_of_website.bulldog_module import bulldog_function
from collection_of_website.glassdor_module import glassdor_function
from collection_of_website.indeed_module import indeed_function
from collection_of_website.infopraca_module import infopraca_function
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
from collection_of_website.ziprecruiter_module import ziprecruiter_function
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
            session.query(NewsOffert.source, func.count(NewsOffert.source))
            .group_by(NewsOffert.source)
            .all()
        )
        for source, count in source_counts:
            print(f"{count}x{source}")
        return
    elif args == "init":
        Base.metadata.create_all(engine)
    else:
        # Deleting last searching data
        session.query(NewsOffert).delete()
        # Deleting data older than 30 days
        session.commit()

    error_list = []
    # Scraping over sites

    
    try:
        adzuna_function(session)
    except Exception as e:
        traceback_list = traceback.extract_tb(e.__traceback__)
        function_name = traceback_list[1].name
        error_list.append(function_name)
    try:
        bulldog_function(session)
    except Exception as e:
        traceback_list = traceback.extract_tb(e.__traceback__)
        function_name = traceback_list[1].name
        error_list.append(function_name)
    
    
    try:
        glassdor_function(session)
    except Exception as e:
        traceback_list = traceback.extract_tb(e.__traceback__)
        function_name = traceback_list[1].name
        error_list.append(function_name)
        
    
    try:
        indeed_function(session)
    except Exception as e:
        traceback_list = traceback.extract_tb(e.__traceback__)
        function_name = traceback_list[1].name
        error_list.append(function_name)

    
    try:
        infopraca_function(session)
    except Exception as e:
        traceback_list = traceback.extract_tb(e.__traceback__)
        function_name = traceback_list[1].name
        error_list.append(function_name)

    
    try:
        just_join_function(session)
    except Exception as e:
        traceback_list = traceback.extract_tb(e.__traceback__)
        function_name = traceback_list[1].name
        error_list.append(function_name)

    
    try:
        linkedin_function(session)
    except Exception as e:
        traceback_list = traceback.extract_tb(e.__traceback__)
        function_name = traceback_list[1].name
        error_list.append(function_name)
    try:
        nofluffjobs_function(session)
    except Exception as e:
        traceback_list = traceback.extract_tb(e.__traceback__)
        function_name = traceback_list[1].name
        error_list.append(function_name)
    try:
        olx_function(session)
    except Exception as e:
        traceback_list = traceback.extract_tb(e.__traceback__)
        function_name = traceback_list[1].name
        error_list.append(function_name)
    try:
        pracodajnia_function(session)
    except Exception as e:
        traceback_list = traceback.extract_tb(e.__traceback__)
        function_name = traceback_list[1].name
        error_list.append(function_name)


    try:
        pracuj_function(session)
    except Exception as e:
        traceback_list = traceback.extract_tb(e.__traceback__)
        function_name = traceback_list[1].name
        error_list.append(function_name)
    
    try:
        rocketjobs_function(session)
    except Exception as e:
        traceback_list = traceback.extract_tb(e.__traceback__)
        function_name = traceback_list[1].name
        error_list.append(function_name)
    try:
        solid_jobs_function(session)
    except Exception as e:
        traceback_list = traceback.extract_tb(e.__traceback__)
        function_name = traceback_list[1].name
        error_list.append(function_name)
    try:
        szukampracy_function(session)
    except Exception as e:
        traceback_list = traceback.extract_tb(e.__traceback__)
        function_name = traceback_list[1].name
        error_list.append(function_name)
    try:
        talent_function(session)
    except Exception as e:
        traceback_list = traceback.extract_tb(e.__traceback__)
        function_name = traceback_list[1].name
        error_list.append(function_name)
    try:
        theprotocol_function(session)
    except Exception as e:
        traceback_list = traceback.extract_tb(e.__traceback__)
        function_name = traceback_list[1].name
        error_list.append(function_name)
    try:
        ziprecruiter_function(session)
    except Exception as e:
        traceback_list = traceback.extract_tb(e.__traceback__)
        function_name = traceback_list[1].name
        error_list.append(function_name)
    
    # Saving results
    session.commit()
    session.close()


    # Clearing terminal
    clear = lambda: os.system("cls" if os.name == "nt" else "clear")
    clear()
    sleep(1)
    # Summary of scrapping
    source_counts = (
        session.query(NewsOffert.source, func.count(NewsOffert.source))
        .group_by(NewsOffert.source)
        .all()
    )
    print("New offert:")
    for source, count in source_counts:
        print(f"{count} x {source}")
    if len(error_list) > 1:
        print(f"Error at: {error_list}")
        winsound.PlaySound("*", winsound.SND_ALIAS)
    else:
        winsound.PlaySound(r"C:\Windows\Media\Speech On.wav", winsound.SND_FILENAME)
