from replayScraper import scrape_recent
import schedule
import time

schedule.every().day.do(scrape_recent, "test.csv")

while True:
    schedule.run_pending()
    time.sleep(1)