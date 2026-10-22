import json
import sqlite3
import csv
import os
from parser import teams, nickname, _rebuild_nickname_lookup, _mon_for_nickname, players, fetch_json
from moveDB import load_ids, replay_id, load_replay_urls
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor

DB_ROOT = Path(__file__).resolve().parent.parent

def create_db(dbName):
    conn = sqlite3.connect(dbName)
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS partners (
                    id DOUBLE REFERENCES monDB(id),
                    partner TEXT DEFAULT NULL,
                    usage DOUBLE DEFAULT 0,
                    PRIMARY KEY (id, partner)
                    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS processed_replays (
                    id TEXT PRIMARY KEY
                    )''')

    conn.commit()
    conn.close()

MON_IDS = load_ids()

def parse_replay(data):
    lines = data["log"].splitlines()
    players["p1"].clear()
    players["p2"].clear()
    teams(lines)

    for mon in players["p1"]:
        for partner in players["p1"]:
            if mon.name != partner.name:
                mon.add_partners([partner.name])
    for mon in players["p2"]:
        for partner in players["p2"]:
            if mon.name != partner.name:
                mon.add_partners([partner.name])

    rows = []
    for side in ("p1", "p2"):
        for mon in players[side]:
            mon_id = MON_IDS.get(mon.name)
            if mon_id is None:
                continue
            rows.extend((mon_id, partner) for partner in mon.get_partners())

    return rows

def print_teams():
    print("Player 1 Team:")
    for mon in players["p1"]:
        print(f"- {mon.name} Partners: {mon.get_partners()}")
    print("\nPlayer 2 Team:")
    for mon in players["p2"]:
        print(f"- {mon.name} Partners: {mon.get_partners()}")

def process_replay(url):
    return replay_id(url), parse_replay(fetch_json(url))

def print_top(dbName, fileName):
    conn = sqlite3.connect(dbName)
    cursor = conn.cursor()
    cursor.execute('''WITH ranked AS (SELECT id, partner, usage, ROW_NUMBER() OVER (PARTITION BY id ORDER BY usage DESC) AS rank FROM partners) SELECT * FROM ranked WHERE rank <= 5''')

    lookup_data = []
    with open(fileName, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "partner", "usage", "rank"])
    for row in cursor.fetchall():   
        with open(fileName, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(row)
        lookup_data.append({
            "id": row[0],
            "partner": row[1],
            "usage": row[2],
            "rank": row[3]
        })
    lookup_data_js = "const partnerData = " + json.dumps(lookup_data, ensure_ascii=True) + ";\n\nexport { partnerData };\n"

    lookup_data_path = DB_ROOT / 'my-react-app' / 'src' / 'js' / 'partner-data.js'
    lookup_data_path.write_text(lookup_data_js, encoding="utf-8")

    conn.close()

def main():
    fileName = DB_ROOT / "DB_CSV" / "replaysDraft.csv"
    dbName = DB_ROOT / "database" / "partnerDB.sqlite"
    dbName2 = DB_ROOT / "database" / "monDB.sqlite"

    create_db(dbName)
    main_conn = sqlite3.connect(dbName2)
    main_processed_ids = {
        row[0] for row in main_conn.execute('SELECT id FROM processed_replays')
    }
    main_conn.close()

    partner_conn = sqlite3.connect(dbName)
    partner_processed_ids = {
        row[0] for row in partner_conn.execute('SELECT id FROM processed_replays')
    }
    partner_conn.close()

    urls = [
        url for url in load_replay_urls(fileName)
        if replay_id(url) in main_processed_ids
        and replay_id(url) not in partner_processed_ids
    ]

    if not urls:
        print("No new processed replays found for partner counting.")
        return

    worker_count = min(16, os.cpu_count() or 1)
    conn = sqlite3.connect(dbName)
    with ProcessPoolExecutor(max_workers=worker_count) as pool:
        for replay, rows in pool.map(process_replay, urls, chunksize=4):
            conn.executemany(
                '''INSERT INTO partners (id, partner, usage) VALUES (?, ?, 1)
                   ON CONFLICT (id, partner) DO UPDATE SET usage = usage + 1''',
                rows,
            )
            conn.execute(
                'INSERT INTO processed_replays (id) VALUES (?)',
                (replay,),
            )
            conn.commit()
    conn.commit()
    conn.close()
    print_top(dbName, DB_ROOT / "DB_CSV" / "partners.csv")

if __name__ == "__main__":
    main()