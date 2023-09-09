from .solid_jobs_module import solid_jobs_function
from .bulldog_module import bulldog_function
from .nofluffjobs_module import nofluffjobs_function
from .pracuj_module import pracuj_function
from .linkedin_module import linkedin_function
from .olx_module import olx_function
from collection_of_website.base_module import NewsOffert
from sqlalchemy import inspect, func
from sqlalchemy.orm import sessionmaker
import time
from .just_join_module import just_join_function
from .base_module import NewsOffert, Base, engine


def collect_offert():
    start = time.perf_counter()
    inspector = inspect(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    if not inspector.has_table(NewsOffert.__tablename__):
        Base.metadata.create_all(engine)
    else:
        session.query(NewsOffert).delete()
        session.commit()

    solid_jobs_function(session)
    bulldog_function(session)
    nofluffjobs_function(session)
    olx_function(session)
    pracuj_function(session)
    just_join_function(session)
    linkedin_function(session)
    session.commit()
    session.close()
    source_counts = session.query(NewsOffert.source, func.count(NewsOffert.source)).group_by(NewsOffert.source).all()

    for source, count in source_counts:
        print(f"{count}x{source}")
    finish = time.perf_counter()
    print(finish-start)