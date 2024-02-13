from collection_of_website.jobs_collector import collect_offert, show_last_result, change_applicated_status
from collection_of_website.base_module import init_database_connection, create_table
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-last", help="Print last value", action="store_true")
    group.add_argument("-init", help="Init new table", action="store_true")
    group.add_argument("-check", help="Change status offert from database to checked", action="store_true")
    args = parser.parse_args()

    session, inspector = init_database_connection()
    if args.init:
        session, inspector = create_table(session)
    elif args.last:
        show_last_result(session)
    elif args.check:
        change_applicated_status(session)
    else:
        collect_offert(session, inspector)
