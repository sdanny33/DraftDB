import sqlite3
import csv
from pathlib import Path
from parser import parse

DB_ROOT = Path(__file__).resolve().parent.parent

def create_db(dbName):
    # Connect to the database. If it doesn't exist, it will be created.
    conn = sqlite3.connect(dbName)
    cursor = conn.cursor()
    # Create a new table called 'users' with columns 'id' and 'name'
    cursor.execute('''CREATE TABLE IF NOT EXISTS mons
                    (id DOUBLE, name TEXT PRIMARY KEY, games_played DOUBLE DEFAULT 0, wins DOUBLE DEFAULT 0, kills DOUBLE DEFAULT 0, deaths DOUBLE DEFAULT 0)''')

    mons_csv_path = DB_ROOT / 'DraftDB' / 'CSV' / 'mons.csv'
    with open(mons_csv_path, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            # Assuming the CSV has columns: id, name
            cursor.execute('INSERT INTO mons (id, name) VALUES (?, ?)', (row[0], row[1]))

    # Commit the changes and close the connection
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

    count = 0
    for link in links_to_process:
        if count % 10 == 0:
            print(f'Parsing {link}...')
        count += 1
        parse(link, dbName)

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

def nothing():
    pass

def main():
    dbName = DB_ROOT / 'database' / 'monDBTest.sqlite'
    replay_csv_path = DB_ROOT / 'CSV' / 'replaysDraftTest.csv'
    archive_csv_path = DB_ROOT / 'CSV' / 'replaysDraft.csv'
    update_db(replay_csv_path, dbName, archive_csv_path)
    update_column(dbName)
    nothing()

if __name__ == "__main__":
    main()
