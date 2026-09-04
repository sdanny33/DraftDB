from parser import *

# parser helper functions

def edges(lines):
    list = ["Urshifu", "Greninja", "Dudunsparce", "Zacian", "Zamazenta", "Necrozma-Dusk-Mane", "Necrozma-Dawn-Wings", "Tauros-Paldea-Combat", "Tauros-Paldea-Blaze", "Tauros-Paldea-Aqua"]
    reset()
    teams(lines)
    for i in range(min(6, len(players["p1"]), len(players["p2"]))):
        if players["p1"][i].name in list or players["p2"][i].name in list:
            reset()
            return True
    reset()
    return False

def reparse(start, end, start_from):
    # If start_from is an int, treat it as a 0-based line index to skip.
    with open(start, 'r') as file:
        for idx, raw in enumerate(file):
            if idx < start_from:
                continue
            url = raw.strip()
            if not url:
                continue

            data = fetch_json(url)
            lines = data["log"].splitlines()
            edge = edges(lines)
            if edge:
                with open(end, 'a') as edge_file:
                    edge_file.write(url + "\n")
                    print(f"Edge found and saved: {url}")

# create db helper functions

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

def subtract_stats(source_db, target_db):
    source_conn = sqlite3.connect(source_db)
    source_cursor = source_conn.cursor()
    source_cursor.execute('SELECT id, games_played, wins, kills, deaths FROM mons')
    stats = {row[0]: row[1:] for row in source_cursor.fetchall()}
    source_conn.close()

    target_conn = sqlite3.connect(target_db)
    target_cursor = target_conn.cursor()
    for mon_id, (games_played, wins, kills, deaths) in stats.items():
        target_cursor.execute('SELECT games_played, wins, kills, deaths FROM mons WHERE id = ?', (mon_id,))
        target_stats = target_cursor.fetchone()
        if target_stats:
            new_games_played = max(0, target_stats[0] - games_played)
            new_wins = max(0, target_stats[1] - wins)
            new_kills = max(0, target_stats[2] - kills)
            new_deaths = max(0, target_stats[3] - deaths)
            target_cursor.execute('UPDATE mons SET games_played = ?, wins = ?, kills = ?, deaths = ? WHERE id = ?', (new_games_played, new_wins, new_kills, new_deaths, mon_id))
    target_conn.commit()
    target_conn.close()

def add_stats(source_db, target_db):
    source_conn = sqlite3.connect(source_db)
    source_cursor = source_conn.cursor()
    source_cursor.execute('SELECT id, games_played, wins, kills, deaths FROM mons')
    stats = {row[0]: row[1:] for row in source_cursor.fetchall()}
    source_conn.close()

    target_conn = sqlite3.connect(target_db)
    target_cursor = target_conn.cursor()
    for mon_id, (games_played, wins, kills, deaths) in stats.items():
        target_cursor.execute('SELECT games_played, wins, kills, deaths FROM mons WHERE id = ?', (mon_id,))
        target_stats = target_cursor.fetchone()
        if target_stats:
            new_games_played = target_stats[0] + games_played
            new_wins = target_stats[1] + wins
            new_kills = target_stats[2] + kills
            new_deaths = target_stats[3] + deaths
            target_cursor.execute('UPDATE mons SET games_played = ?, wins = ?, kills = ?, deaths = ? WHERE id = ?', (new_games_played, new_wins, new_kills, new_deaths, mon_id))
    target_conn.commit()
    target_conn.close()

def add_row(source_db, target_db, mon_id):
    source_conn = sqlite3.connect(source_db)
    source_cursor = source_conn.cursor()
    source_cursor.execute('SELECT games_played, wins, kills, deaths FROM mons WHERE id = ?', (mon_id,))
    source_stats = source_cursor.fetchone()
    source_conn.close()

    if not source_stats:
        return

    target_conn = sqlite3.connect(target_db)
    target_cursor = target_conn.cursor()
    target_cursor.execute('SELECT games_played, wins, kills, deaths FROM mons WHERE id = ?', (mon_id,))
    target_stats = target_cursor.fetchone()

    if target_stats:
        new_games_played = target_stats[0] + source_stats[0]
        new_wins = target_stats[1] + source_stats[1]
        new_kills = target_stats[2] + source_stats[2]
        new_deaths = target_stats[3] + source_stats[3]
        target_cursor.execute('UPDATE mons SET games_played = ?, wins = ?, kills = ?, deaths = ? WHERE id = ?', (new_games_played, new_wins, new_kills, new_deaths, mon_id))

    target_conn.commit()
    target_conn.close()