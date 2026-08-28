import sqlite3
import csv
import zlib
from pathlib import Path
from parser import fetch_json

DB_ROOT = Path(__file__).resolve().parent.parent

def _extract_replay_id(url: str) -> str:
    """Extracts the replay identifier from a URL or raw filename."""
    clean = url.strip().rstrip("/").split("/")[-1]
    return clean.replace(".json", "")

def create_replay_cache_table(dbName):
    """Initializes the compressed cache table using BLOB storage for logs."""
    with sqlite3.connect(dbName) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS replay_cache (
                id TEXT PRIMARY KEY,
                log_blob BLOB NOT NULL
            )
        ''')
        conn.commit()

def save_replay_to_cache(dbName, fileName, batch_size=100):
    create_replay_cache_table(dbName)

    links = []
    with open(fileName, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row and row[0].strip():
                links.append(row[0].strip())

    with sqlite3.connect(dbName) as conn:
        cursor = conn.cursor()
        
        # SQLite performance pragmas
        cursor.execute("PRAGMA journal_mode = WAL;")
        cursor.execute("PRAGMA synchronous = NORMAL;")

        # Load existing cached IDs to skip duplicate fetches instantly
        cursor.execute("SELECT id FROM replay_cache")
        cached_ids = {row[0] for row in cursor.fetchall()}
        print(f"Found {len(cached_ids)} existing replays in cache. Processing {len(links)} total links...")

        inserted_count = 0

        for idx, link in enumerate(links, start=1):
            replay_id = _extract_replay_id(link)
            if replay_id in cached_ids:
                continue

            try:
                data = fetch_json(link)
                log_text = data.get("log", "")
                
                if log_text:
                    # Compress UTF-8 encoded log string to binary bytes
                    compressed_blob = zlib.compress(log_text.encode('utf-8'), level=6)

                    cursor.execute(
                        "INSERT OR IGNORE INTO replay_cache (id, log_blob) VALUES (?, ?)",
                        (replay_id, compressed_blob)
                    )
                    cached_ids.add(replay_id)
                    inserted_count += 1
                    # print(f"[{idx}/{len(links)}] Cached: {replay_id}")

            except Exception as error:
                error_type = type(error).__name__
                print(f"[{idx}/{len(links)}] Failed {link} ({error_type}): {error}")
                continue

            # Batch commit to disk periodically
            if inserted_count > 0 and inserted_count % batch_size == 0:
                print(f"Batch commit: {inserted_count} new replays cached so far...")
                conn.commit()

        conn.commit()
        print(f"Caching complete! Successfully compressed and saved {inserted_count} new replays.")

def get_cached_log(dbName, replay_url_or_id: str) -> list[str]:
    """Helper to retrieve and decompress a battle log by URL or replay ID."""
    replay_id = _extract_replay_id(replay_url_or_id)
    with sqlite3.connect(dbName) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT log_blob FROM replay_cache WHERE id = ?", (replay_id,))
        row = cursor.fetchone()
        if row:
            decompressed_text = zlib.decompress(row[0]).decode('utf-8')
            return decompressed_text.splitlines()
    return []

def main():
    dbName = DB_ROOT / 'database' / 'replaysDB.sqlite'
    fileName = DB_ROOT / 'DB_CSV' / 'replaysDraft.csv'
    save_replay_to_cache(dbName, fileName)

if __name__ == "__main__":
    main()