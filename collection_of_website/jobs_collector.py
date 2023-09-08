from solid_jobs_module import solid_jobs_function
from bulldog_module import bulldog_function
from nofluffjobs_module import nofluffjobs_function
from pracuj_module import pracuj_function
from linkedin_module import linkedin_function
from olx_module import olx_function
from base_module import NewsOffert
from sqlalchemy import inspect
from sqlalchemy.orm import sessionmaker

from just_join_module import just_join_function
from base_module import NewsOffert, Base, engine


def collect_offert():
    inspector = inspect(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    if not inspector.has_table(NewsOffert.__tablename__):
        Base.metadata.create_all(engine)

    solid_jobs_function(session)
    bulldog_function(session)
    nofluffjobs_function(session)
    olx_function(session)
    pracuj_function(session)
    just_join_function(session)
    linkedin_function(session)
    session.commit()
    session.close()

### Printing result
"""
dupa = session.query(NewsOffert).filter(NewsOffert.source=="Bulldog").count()
dupa2 = session.query(NewsOffert).filter(NewsOffert.source=="Solid Jobs").count()
dupa3 = session.query(NewsOffert).filter(NewsOffert.source=="NoFluffJobs").count()
dupa4 = session.query(NewsOffert).filter(NewsOffert.source=="Olx").count()
dupa5 = session.query(NewsOffert).filter(NewsOffert.source=="Pracuj.pl").count()
dupa6 = session.query(NewsOffert).filter(NewsOffert.source=="Just Join").count()
dupa7 = session.query(NewsOffert).filter(NewsOffert.source=="Linkedin").count()

session.close()
"""
collect_offert()