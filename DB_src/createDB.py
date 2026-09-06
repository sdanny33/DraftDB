import sqlite3
import csv
import socket
import urllib.error
from pathlib import Path
from parser import parse, parse_lines
from replaySaver import decompress_cached_log, save_replay_to_cache
import re

DB_ROOT = Path(__file__).resolve().parent.parent

def _is_timeout_exception(error):
    current = error
    seen = set()

    while current is not None and id(current) not in seen:
        seen.add(id(current))

        if isinstance(current, (TimeoutError, socket.timeout)):
            return True

        if isinstance(current, urllib.error.URLError):
            reason = current.reason
            if isinstance(reason, (TimeoutError, socket.timeout)):
                return True
            if isinstance(reason, str) and "timed out" in reason.lower():
                return True

        message = str(current).lower()
        if "timed out" in message or "timeout" in message:
            return True

        current = current.__cause__ or current.__context__

    return False

def create_db(dbName):
    # Connect to the database. If it doesn't exist, it will be created.
    conn = sqlite3.connect(dbName)
    cursor = conn.cursor()
    # Create a new table with `sprite` as a BLOB to store PNG bytes.
    cursor.execute('''CREATE TABLE IF NOT EXISTS mons
                    (id DOUBLE, sprite BLOB, name TEXT PRIMARY KEY, points INTEGER DEFAULT 0, games_played DOUBLE DEFAULT 0, wins DOUBLE DEFAULT 0, winrate DOUBLE DEFAULT 0, kills INTEGER DEFAULT 0, deaths INTEGER DEFAULT 0, diff INTEGER DEFAULT 0, KPG DOUBLE DEFAULT 0, damage DOUBLE DEFAULT 0, healing DOUBLE DEFAULT 0, avg_damage DOUBLE DEFAULT 0, avg_healing DOUBLE DEFAULT 0, path TEXT DEFAULT NULL)''')

    mons_csv_path = DB_ROOT / 'DB_CSV' / 'mons.csv'
    with open(mons_csv_path, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            # Assuming the CSV has columns: id, name, points
            cursor.execute('INSERT INTO mons (id, name, points) VALUES (?, ?, ?)', (row[0], row[1], row[2]))
    
    # Commit the changes and close the connection
    conn.commit()
    conn.close()

def _sprite_stem(mon_id):
    if bool(re.search(r'\.00\d$', str(mon_id))):
        return str(mon_id)
    return str(int(float(mon_id)))

def add_sprites(dbName):
    conn = sqlite3.connect(dbName)
    cursor = conn.cursor()
    sprite_path = DB_ROOT / 'sprites'
    cursor.execute('SELECT id FROM mons')
    for i in cursor.fetchall():
        sprite_name = _sprite_stem(i[0])
        sprite_file = sprite_path / f'{sprite_name}.png'
        default_file = sprite_path / '0.png'
        with open(default_file, 'rb') as fh:
            blob = fh.read()
        cursor.execute('UPDATE mons SET path = ? WHERE id = ?', (f'sprites/{sprite_name}.png' if sprite_file.exists() else 'sprites/0.png', i[0]))
        cursor.execute('UPDATE mons SET sprite = ? WHERE id = ?', (blob, i[0]))
        if sprite_file.exists():
            with open(sprite_file, 'rb') as fh:
                blob = fh.read()
            cursor.execute('UPDATE mons SET path = ? WHERE id = ?', (f'sprites/{sprite_name}.png', i[0]))
            cursor.execute('UPDATE mons SET sprite = ? WHERE id = ?', (blob, i[0]))

    conn.commit()
    conn.close()

def add_column(dbName, column_name, column_type, default_value):
    conn = sqlite3.connect(dbName)
    cursor = conn.cursor()
    cursor.execute(f'ALTER TABLE mons ADD COLUMN {column_name} {column_type} DEFAULT {default_value}')
    conn.commit()
    conn.close()

def update_links(fileName, outName):
    links = []
    with open(fileName, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row:
                links.append(row[0])

    if not links:
        return

    # links[0] is the previous run's root marker and links[1] becomes the next root.
    # Only process truly new links to avoid adding roots twice across runs.
    links_to_process = links[2:] if len(links) > 2 else []

    if not links_to_process:
        return

    with open(outName, 'a', newline='') as file:
        writer = csv.writer(file)
        for link in links_to_process:
            writer.writerow([link])

    # Keep the original second row as the new first row for the next run.
    next_seed = links[1] if len(links) > 1 else links[0]
    with open(fileName, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([next_seed])

def update_column(dbName):
    conn = sqlite3.connect(dbName)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE mons
        SET winrate = CASE
            WHEN games_played = 0 THEN 0
            ELSE ROUND((wins * 100.0) / games_played, 2)
        END
    ''')
    cursor.execute('UPDATE mons SET diff = kills - deaths')
    cursor.execute('''UPDATE mons set KPG = CASE
        WHEN games_played = 0 THEN 0
        ELSE ROUND((kills) / games_played, 2)
    END''')
    cursor.execute('''UPDATE mons set avg_damage = CASE
        WHEN games_played = 0 THEN 0
        ELSE ROUND((damage) / games_played, 2)
    END''')
    cursor.execute('''UPDATE mons set avg_healing = CASE
        WHEN games_played = 0 THEN 0
        ELSE ROUND((healing) / games_played, 2)
    END''')
    conn.commit()
    conn.close()

def refresh(dbName):
    conn = sqlite3.connect(dbName)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS mons_new
                    (id DOUBLE, name TEXT PRIMARY KEY, games_played DOUBLE DEFAULT 0, wins DOUBLE DEFAULT 0, winrate DOUBLE DEFAULT 0, kills INTEGER DEFAULT 0, deaths INTEGER DEFAULT 0, diff INTEGER DEFAULT 0)''')
    cursor.execute('INSERT INTO mons_new (id, name, games_played, wins, kills, deaths) SELECT id, name, games_played, wins, kills, deaths FROM mons')
    cursor.execute('DROP TABLE mons')
    cursor.execute('ALTER TABLE mons_new RENAME TO mons')
    conn.commit()
    conn.close()

def reset_db(dbName):
    conn = sqlite3.connect(dbName)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM mons')
    conn.commit()
    conn.close()

def get_stats(replay_db, dbName):
    replay_db = Path(replay_db)
    replay_dbs = sorted(replay_db.glob('replays_part*.sqlite')) if replay_db.is_dir() else [replay_db]
    conn2 = sqlite3.connect(dbName)
    cursor2 = conn2.cursor()

    try:
        for replay_shard in replay_dbs:
            with sqlite3.connect(replay_shard) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT id, log_blob FROM replay_cache')
                for row in cursor.fetchall():
                    lines = decompress_cached_log(row[1])
                    parse_lines(lines, cursor=cursor2)
            conn2.commit()
    finally:
        conn2.close()


def main():
    db_dir = DB_ROOT / 'database'
    dbName = DB_ROOT / 'database' / 'monDB.sqlite'
    replay_csv_path = DB_ROOT / 'DB_CSV' / 'replaysDraftTest.csv'
    archive_csv_path = DB_ROOT / 'DB_CSV' / 'replaysDraft.csv'
    update_links(replay_csv_path, archive_csv_path)
    save_replay_to_cache(db_dir=db_dir, file_name=archive_csv_path)
    get_stats(db_dir, dbName)
    update_column(dbName)

if __name__ == "__main__":
    main()
