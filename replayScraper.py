import json
import urllib.request
import csv
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

def main():
    # scrape_all("replaysDraft.csv")
    scrape_recent("test.csv")

if __name__ == "__main__":
    main()