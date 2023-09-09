from collection_of_website.jobs_collector import collect_offert
import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-last", help="Print last value", action="store_true")
    args = parser.parse_args()
    collect_offert(args.last)