import sqlite3

def create_db(dbName):
    conn = sqlite3.connect(dbName)
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS moves (
                    id INTEGER REFERENCES monDB(id),
                    move TEXT DEFAULT NULL,
                    usage DOUBLE DEFAULT 0,
                    PRIMARY KEY (id, move)
                    )''')

    conn.commit()
    conn.close()

