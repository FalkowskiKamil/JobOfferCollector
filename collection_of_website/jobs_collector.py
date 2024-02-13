import os

from sqlalchemy import func

from importlib import import_module
from time import sleep

from collection_of_website.base_module import Base, create_table, NewsOffert


def collect_offert(session, inspector):
    # Checking db
    if not inspector.has_table(NewsOffert.__tablename__):
        session, inspector = create_table(session)
    # Deleting last searching data
    session.query(NewsOffert).delete()

    list_of_dir = os.listdir("collection_of_website")
    list_of_dir.remove("base_module.py")
    list_of_dir.remove("jobs_collector.py")

    error_list = []
    for module in list_of_dir:
        module = module.removesuffix(".py")
        module_name = f'collection_of_website.{module.removesuffix(".py")}'
        imported_module = import_module(module_name)
        function_name = f'{module.removesuffix("_module")}_function'
        function = getattr(imported_module, function_name)
        try:
            session = function(session, inspector)
        except Exception as e:
            error_list.append(function_name)
    clearing_terminal()
    if len(error_list) > 0:
        print(f'List of error: {error_list}')
    # Saving results
    session.commit()
    session.close()


def change_applicated_status(session):
    # Iterate through all mapped classes and update "applicated" column to True
    for table in Base.metadata.tables.values():
        session.query(table).update({"applicated": True})
    session.commit()
    session.close()
    return print("Successfully changed status to checked")


def show_last_result(session):
    result = session.query(NewsOffert.source, func.count(NewsOffert.source)).group_by(NewsOffert.source).all()
    for source, count in result:
        print(f"Source: {source}, Count: {count}")


def clearing_terminal():
    sleep(0.5)
    os.system("cls" if os.name == "nt" else "clear")
    sleep(0.5)
