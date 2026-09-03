import sqlite3
import csv
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import zstandard as zstd
from parser import teams, print_stats, _rebuild_nickname_lookup, nickname, fetch_json, players

DB_ROOT = Path(__file__).resolve().parent.parent

# Prefixes to strip: rules, infoboxes, team previews, inactive timers, chat, and spectator joins/leaves
DROP_PREFIXES = (
    "|rule|",
    "|raw|",
    "|teampreview",
    "|inactive|",
    "|inactiveoff|",
    "|j|",
    "|l|",
    "|c|",
    "|c:|",
    "|t:|",
)

def _extract_replay_id(url: str) -> str:
    """Extracts the clean replay identifier from a URL or filename."""
    clean = url.strip().rstrip("/").split("/")[-1]
    return clean.replace(".json", "")

def clean_battle_log(raw_log: str) -> str:
    """Strips unnecessary protocol lines to reduce payload size."""
    cleaned = []
    for line in raw_log.splitlines():
        trimmed = line.strip()
        if not trimmed or trimmed == "|" or trimmed == "|upkeep":
            continue
        if any(trimmed.startswith(prefix) for prefix in DROP_PREFIXES):
            continue
        cleaned.append(trimmed)
    return "\n".join(cleaned)

def create_replay_cache_table(db_path: Path):
    """Creates the cache table in the target SQLite database."""
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS replay_cache (
                id TEXT PRIMARY KEY,
                log_blob BLOB NOT NULL
            )
        ''')
        conn.commit()

def _fetch_and_compress(link: str) -> tuple[str, bytes | None, Exception | None]:
    """Worker task: Fetches JSON, strips metadata, and compresses with a thread-local zstd context."""
    replay_id = _extract_replay_id(link)
    try:
        data = fetch_json(link)
        raw_log = data.get("log", "")
        if not raw_log:
            return replay_id, None, None

        cleaned_log = clean_battle_log(raw_log)
        raw_bytes = cleaned_log.encode("utf-8")
        if not raw_bytes:
            return replay_id, None, None

        compressor = zstd.ZstdCompressor(level=19, write_content_size=True)
        compressed_blob = compressor.compress(raw_bytes)
        return replay_id, compressed_blob, None
    except Exception as exc:
        return replay_id, None, exc

def save_replay_to_cache(db_dir: Path, file_name: Path, batch_size: int = 100, max_workers: int = 16, max_rows_per_db: int = 50_000):
    """Fetches, compresses, and saves replays directly into 50k-row sharded databases."""
    db_dir.mkdir(parents=True, exist_ok=True)

    links = []
    with open(file_name, "r") as file:
        reader = csv.reader(file)
        for row in reader:
            if row and row[0].strip():
                links.append(row[0].strip())

    if not links:
        print("No replay links found in CSV.")
        return

    # Check all existing shards to skip duplicate fetches
    cached_ids = set()
    existing_shards = sorted(db_dir.glob("replays_part*.sqlite"))
    
    for shard in existing_shards:
        with sqlite3.connect(shard) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='replay_cache'")
            if cursor.fetchone():
                cursor.execute("SELECT id FROM replay_cache")
                cached_ids.update(row[0] for row in cursor.fetchall())

    pending_links = [l for l in links if _extract_replay_id(l) not in cached_ids]
    print(f"Found {len(cached_ids):,} existing cached replays. Fetching {len(pending_links):,} remaining links across {max_workers} threads...")

    if not pending_links:
        print("All replays are already cached.")
        return

    # Determine current active shard and current row count
    current_part = len(existing_shards) if existing_shards else 1
    current_db_path = db_dir / f"replays_part{current_part}.sqlite"
    create_replay_cache_table(current_db_path)

    with sqlite3.connect(current_db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM replay_cache")
        current_shard_count = cursor.fetchone()[0]

    if current_shard_count >= max_rows_per_db:
        current_part += 1
        current_db_path = db_dir / f"replays_part{current_part}.sqlite"
        create_replay_cache_table(current_db_path)
        current_shard_count = 0

    inserted_total = 0
    buffer = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_link = {
            executor.submit(_fetch_and_compress, link): link
            for link in pending_links
        }

        for future in as_completed(future_to_link):
            replay_id, compressed_blob, error = future.result()

            if error:
                print(f"Failed {replay_id} ({type(error).__name__}): {error}")
                continue

            if compressed_blob is not None:
                buffer.append((replay_id, compressed_blob))
                inserted_total += 1

                if inserted_total % 100 == 0 or inserted_total == len(pending_links):
                    print(f"[{inserted_total}/{len(pending_links)}] Cached & compressed: {replay_id}")

            # Flush buffer when batch size is met
            if len(buffer) >= batch_size:
                # Rotate shard if full
                if current_shard_count + len(buffer) > max_rows_per_db:
                    space_left = max_rows_per_db - current_shard_count
                    to_current = buffer[:space_left]
                    to_next = buffer[space_left:]

                    with sqlite3.connect(current_db_path) as conn:
                        conn.executemany("INSERT OR IGNORE INTO replay_cache (id, log_blob) VALUES (?, ?)", to_current)
                        conn.commit()

                    current_part += 1
                    current_db_path = db_dir / f"replays_part{current_part}.sqlite"
                    create_replay_cache_table(current_db_path)
                    current_shard_count = 0

                    if to_next:
                        with sqlite3.connect(current_db_path) as conn:
                            conn.executemany("INSERT OR IGNORE INTO replay_cache (id, log_blob) VALUES (?, ?)", to_next)
                            conn.commit()
                        current_shard_count = len(to_next)
                else:
                    with sqlite3.connect(current_db_path) as conn:
                        conn.executemany("INSERT OR IGNORE INTO replay_cache (id, log_blob) VALUES (?, ?)", buffer)
                        conn.commit()
                    current_shard_count += len(buffer)

                buffer.clear()

    # Flush remaining records
    if buffer:
        with sqlite3.connect(current_db_path) as conn:
            conn.executemany("INSERT OR IGNORE INTO replay_cache (id, log_blob) VALUES (?, ?)", buffer)
            conn.commit()

    print(f"\nCaching complete! Successfully saved {inserted_total} new replays across sharded databases.")

def get_cached_log(db_dir: Path, replay_url_or_id: str) -> str:
    """Scans all shard files (replays_part*.sqlite) to find and decompress the battle log."""
    replay_id = _extract_replay_id(replay_url_or_id)
    decompressor = zstd.ZstdDecompressor()

    for shard_path in sorted(db_dir.glob("replays_part*.sqlite")):
        with sqlite3.connect(shard_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT log_blob FROM replay_cache WHERE id = ?", (replay_id,))
            row = cursor.fetchone()
            if row and row[0]:
                return decompress_cached_log(row[0])
    return "Replay not found in cache."

def decompress_cached_log(blob: bytes) -> list[str]:
    """Decompress a replay cache blob into parser-ready log lines."""
    decompressor = zstd.ZstdDecompressor()
    try:
        text = decompressor.decompress(blob, max_output_size=1024 * 1024).decode("utf-8")
    except zstd.ZstdError:
        text = decompressor.stream_reader(blob).read().decode("utf-8")
    return text.splitlines()

def split_database_by_rows(source_db_path: Path, max_rows: int = 50_000):
    if not source_db_path.exists():
        print(f"Source database not found at: {source_db_path}")
        return

    output_dir = source_db_path.parent

    with sqlite3.connect(source_db_path) as src_conn:
        src_cursor = src_conn.cursor()
        src_cursor.execute("SELECT COUNT(*) FROM replay_cache")
        total_rows = src_cursor.fetchone()[0]

        if total_rows == 0:
            print("No rows found in source replay_cache.")
            return

        print(f"Found {total_rows} total rows. Splitting into shards of max {max_rows:,} rows each...")

        # Cursor server-side iteration without loading entire database to RAM
        src_cursor.execute("SELECT id, log_blob FROM replay_cache")

        part_num = 1
        while True:
            batch = src_cursor.fetchmany(max_rows)
            if not batch:
                break

            shard_path = output_dir / f"replays_part{part_num}.sqlite"
            if shard_path.exists():
                shard_path.unlink()  # Remove existing shard to write fresh

            print(f"Writing {len(batch):,} rows to {shard_path.name}...")

            with sqlite3.connect(shard_path) as shard_conn:
                shard_conn.execute("PRAGMA journal_mode = WAL;")
                shard_conn.execute("PRAGMA synchronous = NORMAL;")
                shard_conn.execute("""
                    CREATE TABLE IF NOT EXISTS replay_cache (
                        id TEXT PRIMARY KEY,
                        log_blob BLOB NOT NULL
                    )
                """)

                shard_conn.executemany(
                    "INSERT OR IGNORE INTO replay_cache (id, log_blob) VALUES (?, ?)",
                    batch
                )
                shard_conn.commit()
                shard_conn.execute("VACUUM;")

            size_mb = shard_path.stat().st_size / (1024 * 1024)
            print(f"Created {shard_path.name} ({size_mb:.2f} MB)")
            part_num += 1

    print("\nSplitting complete!")

def main():
    db_directory = DB_ROOT / "database"
    csv_file = DB_ROOT / "DB_CSV" / "replaysDraft.csv"
    save_replay_to_cache(
        db_dir=db_directory,
        file_name=csv_file,
        batch_size=100,
        max_workers=16,
        max_rows_per_db=50_000
    )

if __name__ == "__main__":
    main()