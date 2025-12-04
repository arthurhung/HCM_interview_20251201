from logger_setup import get_logger
from csv_helper import CSVHelper
from crawler import HealthMythCrawler


def main():
    logger = get_logger()

    fieldnames = [
        "pid",
        "title",
        "url",
        "publish_date",
        "update_date",
        "content",
    ]

    storage = CSVHelper("hpa_health_myths.csv", fieldnames, logger=logger)
    crawler = HealthMythCrawler(storage=storage, logger=logger)
    crawler.run(initial_n=10, max_pages=5)


if __name__ == "__main__":
    main()
