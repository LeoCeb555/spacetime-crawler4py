import atexit
from configparser import ConfigParser
from argparse import ArgumentParser

from utils.server_registration import get_cache_server
from utils.config import Config
from crawler import Crawler
import report  

# This function runs automatically on keyboard interrupt
def print_final_report():
    print("\n--- CRAWLER STOPPED. GENERATING FINAL REPORT ---")
    try:
        report.makeReport()
    except Exception as e:
        print(f"Error generating report: {e}")

# Register the function
atexit.register(print_final_report)

def main(config_file, restart):
    cparser = ConfigParser()
    cparser.read(config_file)
    config = Config(cparser)
    config.cache_server = get_cache_server(config, restart)
    crawler = Crawler(config, restart)
    crawler.start()


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--restart", action="store_true", default=False)
    parser.add_argument("--config_file", type=str, default="config.ini")
    args = parser.parse_args()
    main(args.config_file, args.restart)