import sqlite3
import csv
import os
from parser import teams, nickname, _rebuild_nickname_lookup, _mon_for_nickname, players, fetch_json
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor

DB_ROOT = Path(__file__).resolve().parent.parent

def create_db(dbName):
    conn = sqlite3.connect(dbName)
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS moves (
                    id DOUBLE REFERENCES monDB(id),
                    move TEXT DEFAULT NULL,
                    usage DOUBLE DEFAULT 0,
                    PRIMARY KEY (id, move)
                    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS processed_replays (
                    id TEXT PRIMARY KEY
                    )''')

    conn.commit()
    conn.close()

def move(lines):
    for line in lines:
        if line.startswith("|move|"):
            parts = line.split("|")
            nickname = parts[2]
            move = parts[3].strip("|")
            mon = _mon_for_nickname(nickname)
            if mon is not None and move not in mon.moves:
                mon.add_moves([move])

def load_ids():
    ids = {}
    with open(DB_ROOT / "DB_CSV" / "mons.csv", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split(",")
            ids.setdefault(parts[1], parts[0])
    return ids

MON_IDS = load_ids()

def replay_id(url):
    return url.strip().rstrip("/").rsplit("/", 1)[-1].removesuffix(".json")

def load_replay_urls(file_name):
    urls = []
    seen_ids = set()
    with open(file_name, newline="", encoding="utf-8") as f:
        for row in csv.reader(f):
            if not row:
                continue
            url = row[0].strip()
            if not url:
                continue
            current_id = replay_id(url)
            if current_id not in seen_ids:
                urls.append(url)
                seen_ids.add(current_id)
    return urls

def parse_replay(data):
    lines = data["log"].splitlines()
    players["p1"].clear()
    players["p2"].clear()
    teams(lines)
    nickname(lines)
    _rebuild_nickname_lookup()
    move(lines)

    rows = []
    for i in range(min(6, len(players["p1"]), len(players["p2"]))):
        for mon in (players["p1"][i], players["p2"][i]):
            mon_id = MON_IDS.get(mon.name)
            if mon_id is None:
                continue
            for moves in mon.moves:
                rows.append((mon_id, moves))
    return rows

def process_replay(url):
    return replay_id(url), parse_replay(fetch_json(url))

def main():
    fileName = DB_ROOT / "DB_CSV" / "replaysDraft.csv"
    dbName = DB_ROOT / "database" / "moveDB.sqlite"
    dbName2 = DB_ROOT / "database" / "monDB.sqlite"

    create_db(dbName)
    main_conn = sqlite3.connect(dbName2)
    main_processed_ids = {
        row[0] for row in main_conn.execute('SELECT id FROM processed_replays')
    }
    main_conn.close()

    move_conn = sqlite3.connect(dbName)
    move_processed_ids = {
        row[0] for row in move_conn.execute('SELECT id FROM processed_replays')
    }
    move_conn.close()

    urls = [
        url for url in load_replay_urls(fileName)
        if replay_id(url) in main_processed_ids
        and replay_id(url) not in move_processed_ids
    ]

    if not urls:
        print("No new processed replays found for move counting.")
        return

    worker_count = min(16, os.cpu_count() or 1)
    conn = sqlite3.connect(dbName)
    with ProcessPoolExecutor(max_workers=worker_count) as pool:
        for replay, rows in pool.map(process_replay, urls, chunksize=4):
            conn.executemany(
                '''INSERT INTO moves (id, move, usage) VALUES (?, ?, 1)
                   ON CONFLICT (id, move) DO UPDATE SET usage = usage + 1''',
                rows,
            )
            conn.execute(
                'INSERT INTO processed_replays (id) VALUES (?)',
                (replay,),
            )
            conn.commit()
    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()