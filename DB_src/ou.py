import json
import urllib.request
import csv
import time
from pathlib import Path

DB_ROOT = Path(__file__).resolve().parent.parent
def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as response:
        html = response.read().decode('utf-8')
        data = json.loads(html)
        return data

def scrape_time(fileName, startTime, endTime):
    current_time = startTime

    with open(fileName, 'a', newline='') as file:
        writer = csv.writer(file)
        while current_time > endTime:
            url = f"https://replay.pokemonshowdown.com/search.json?format=gen9ou&before={current_time}"
            data = fetch_json(url)

            if data is None or len(data) == 0:
                print("No more data available.")
                break
            
            ids = [item["id"] for item in data]
            times = [item["uploadtime"] for item in data]
            time = min(times)

            writer.writerows([[replay_id] for replay_id in ids])
            file.flush()
            current_time = time

def main():
    fileName = DB_ROOT / "DB_CSV" / "gen9ou_replay_ids.csv"
    startTime = 1700000000  # Example start time
    endTime = 1600000000    # Example end time
    scrape_time(fileName, startTime, endTime)

if __name__ == "__main__":
    main()