import json
import urllib.request
import csv
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor 

DB_ROOT = Path(__file__).resolve().parent.parent
def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as response:
        html = response.read().decode('utf-8')
        data = json.loads(html)
        return data

def scrape_all(fileName):
    for i in range(1, 101):
        url = f"https://replay.pokemonshowdown.com/search.json?format=gen9draft&page={i}"
        data = fetch_json(url)
        print(f"Fetched page {i} with {len(data)} replays.")
        ids = [item["id"] for item in data]
        with open(fileName, 'a', newline='') as file:
            writer = csv.writer(file)
            for id in ids:
                replay_url = f"https://replay.pokemonshowdown.com/{id}.json"
                writer.writerow([replay_url])

def fetch_replay(replay_id):
    return f"https://replay.pokemonshowdown.com/{replay_id}.json"

def scrape_time(fileName, startTime, endTime, workers=8):
    time = startTime
    with open(fileName, 'a', newline='') as file, ThreadPoolExecutor(max_workers=workers) as pool:
        writer = csv.writer(file)
        while time > endTime:
            url = f"https://replay.pokemonshowdown.com/search.json?format=gen9ou&before={time}"
            data = fetch_json(url)

            ids = [item["id"] for item in data]
            times = [item["uploadtime"] for item in data]

            for url in pool.map(fetch_replay, ids):
                writer.writerow([url])

            time = min(times)

def scrape_recent(fileName):
    existing_urls = set()
    with open(fileName, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row:
                existing_urls.add(row[0])

    appended_urls = set()
    for i in range(1, 101):
        url = f"https://replay.pokemonshowdown.com/search.json?format=gen9draft&page={i}"
        data = fetch_json(url)
        print(f"Fetched page {i} with {len(data)} replays.")
        ids = [item["id"] for item in data]
        with open(fileName, 'a', newline='') as file:
            writer = csv.writer(file)
            for id in ids:
                replay_url = f"https://replay.pokemonshowdown.com/{id}.json"
                if replay_url in existing_urls:
                    return
                if replay_url in appended_urls:
                    continue
                writer.writerow([replay_url])
                appended_urls.add(replay_url)

def test():
    replay_csv_path = DB_ROOT / 'DB_CSV' / 'replaysOU.csv'
    scrape_time(replay_csv_path, 1793290227, 1669329600)

def main():
    replay_csv_path = DB_ROOT / 'DB_CSV' / 'replaysDraftTest.csv'
    scrape_recent(replay_csv_path)

if __name__ == "__main__":
    test()