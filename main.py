from collection_of_website.jobs_collector import collect_offert
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-last", help="Print last value", action="store_true")
    group.add_argument("-init", help="Init new table", action="store_true")
    args = parser.parse_args()
    
    if args.init:
        action = "init"
    elif args.last:
        action = "last"
    else:
        action = None

    collect_offert(action)
