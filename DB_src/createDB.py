import sqlite3
import csv
import socket
import urllib.error
from pathlib import Path
from parser import parse

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
                    (id DOUBLE, sprite BLOB, name TEXT PRIMARY KEY, points INTEGER DEFAULT 0, games_played DOUBLE DEFAULT 0, wins DOUBLE DEFAULT 0, winrate DOUBLE DEFAULT 0, kills INTEGER DEFAULT 0, deaths INTEGER DEFAULT 0, diff INTEGER DEFAULT 0)''')

    mons_csv_path = DB_ROOT / 'DB_CSV' / 'mons.csv'
    with open(mons_csv_path, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            # Assuming the CSV has columns: id, name, points
            cursor.execute('INSERT INTO mons (id, name, points) VALUES (?, ?, ?)', (row[0], row[1], row[2]))
    
    # Commit the changes and close the connection
    conn.commit()
    conn.close()

def add_sprites(dbName):
    conn = sqlite3.connect(dbName)
    cursor = conn.cursor()
    sprite_path = DB_ROOT / 'images'
    cursor.execute('SELECT id FROM mons')
    for i in cursor.fetchall():
        index = int(i[0])
        default_index = i[0]
        sprite_file = sprite_path / f'{index}.png'
        default_file = sprite_path / '0.png'
        with open(default_file, 'rb') as fh:
            blob = fh.read()
        cursor.execute('UPDATE mons SET sprite = ? WHERE id = ?', (blob, default_index))
        if sprite_file.exists():
            with open(sprite_file, 'rb') as fh:
                blob = fh.read()
            cursor.execute('UPDATE mons SET sprite = ? WHERE id = ?', (blob, index))

    conn.commit()
    conn.close()

def update_db(fileName, dbName, outName):
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

    successful_links = []

    with sqlite3.connect(dbName) as conn:
        cursor = conn.cursor()
        count = 0
        for link in links_to_process:
            count += 1

            try:
                parse(link, cursor=cursor)
                successful_links.append(link)
            except Exception as error:
                error_type = type(error).__name__
                error_message = str(error).strip() or "(no error message)"
                timeout_tag = "timeout" if _is_timeout_exception(error) else "error"
                print(f'Skipping replay ({timeout_tag}): {link} | {error_type}: {error_message}')
                continue

            if count % 100 == 0:
                print(f'Parsing {link}...')
                conn.commit()

        conn.commit()

    with open(outName, 'a', newline='') as file:
        writer = csv.writer(file)
        for link in successful_links:
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

def copy_stats(source_db, target_db):
    source_conn = sqlite3.connect(source_db)
    source_cursor = source_conn.cursor()
    source_cursor.execute('SELECT id, games_played, wins, kills, deaths FROM mons')
    stats = {row[0]: row[1:] for row in source_cursor.fetchall()}
    source_conn.close()

    target_conn = sqlite3.connect(target_db)
    target_cursor = target_conn.cursor()
    for mon_id, (games_played, wins, kills, deaths) in stats.items():
        target_cursor.execute('UPDATE mons SET games_played = ?, wins = ?, kills = ?, deaths = ? WHERE id = ?', (games_played, wins, kills, deaths, mon_id))
    target_conn.commit()
    target_conn.close()

def nothing():
    pass

def main():
    dbName = DB_ROOT / 'database' / 'monDB.sqlite'
    replay_csv_path = DB_ROOT / 'DB_CSV' / 'replaysDraftTest.csv'
    archive_csv_path = DB_ROOT / 'DB_CSV' / 'replaysDraft.csv'
    update_db(replay_csv_path, dbName, archive_csv_path)
    update_column(dbName)
    nothing()

if __name__ == "__main__":
    main()
