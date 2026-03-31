import sqlite3
import csv
from parser import parse

def create_db(dbName):
    # Connect to the database. If it doesn't exist, it will be created.
    conn = sqlite3.connect(dbName)
    cursor = conn.cursor()
    # Create a new table called 'users' with columns 'id' and 'name'
    cursor.execute('''CREATE TABLE IF NOT EXISTS mons
                    (id DOUBLE, name TEXT PRIMARY KEY, games_played DOUBLE DEFAULT 0, wins DOUBLE DEFAULT 0, kills DOUBLE DEFAULT 0, deaths DOUBLE DEFAULT 0)''')

    with open('mons.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            # Assuming the CSV has columns: id, name
            cursor.execute('INSERT INTO mons (id, name) VALUES (?, ?)', (row[0], row[1]))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

def update_db(fileName, dbName):
    # Read links from CSV file
    links = []
    with open(fileName, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            links.append(row[0])
    count = 0
    for link in links:
        if count % 10 == 0:
            print(f'Parsing {link}...')
        count += 1
        parse(link, dbName)

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
    dbName = "monDBTest.sqlite"
    update_db("test.csv", dbName)
    update_column(dbName)
    nothing()

if __name__ == "__main__":
    main()
