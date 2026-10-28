import sqlite3
from parser import (
    teams,
    nickname,
    reset,
    fetch_json,
    actors,
    _mon_for_nickname,
    _rebuild_nickname_lookup,
    players,
)


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

def passive_dmg(lines):
    actor1 = None
    actor2 = None
    hazard_sources = {"p1": {}, "p2": {}}
    status_sources = {}
    passive_moves = {"Stealth Rock", "Spikes", "Toxic Spikes"}
    passive_statuses = {"psn", "brn"}

    def side_for(mon):
        for side in ("p1", "p2"):
            if mon in players[side]:
                return side
        return None

    for line in lines:
        if line.startswith("|switch|"):
            parts = line.split("|")
            mon = _mon_for_nickname(parts[2])
            if mon is not None and len(parts) > 4:
                mon.set_current_hp(int(parts[4].split("/")[0]))

        if line.startswith("|move|"):
            parts = line.split("|")
            actor1_name, actor2_name = actors(line)
            actor1 = _mon_for_nickname(actor1_name)
            actor2 = _mon_for_nickname(actor2_name)
            move = parts[3].strip()
            if actor1 is not None and move in passive_moves:
                actor1.add_hazard(move)
                side = side_for(actor1)
                if side is not None:
                    hazard_sources[side][move] = actor1
        if line.startswith("|-status"):
            parts = line.split("|")
            target_nickname = parts[2]
            target = _mon_for_nickname(target_nickname)
            status = parts[3].strip()
            if status == "tox":
                status = "psn"
            if target is not None:
                target.set_status(status)
            status_source = None
            for part in parts[4:]:
                if "[of]" in part:
                    status_source = _mon_for_nickname(
                        part.split("[of]", 1)[1].strip()
                    )
                    break
            if status_source is None and actor1 is not None and actor1 is not target:
                status_source = actor1
            if status in passive_statuses and status_source is not None:
                status_sources[target_nickname] = status_source
            if actor1 is not None and target is not None:
                actor1.add_hazard(status + "*" + target.name)
        if line.startswith("|-damage"):
            parts = line.split("|")
            nickname_val = parts[2]
            hp_str = parts[3]
            is_passive = any("[from]" in p for p in parts[4:])

            mon = _mon_for_nickname(nickname_val)
            if mon is None:
                continue

            current_hp = 0 if "fnt" in hp_str else int(hp_str.split("/")[0])
            damage = mon.get_current_hp() - current_hp
            mon.set_current_hp(current_hp)

            if is_passive and damage > 0:
                passive = next(
                    (part.split("[from]", 1)[1].strip()
                     for part in parts[4:] if "[from]" in part),
                    None,
                )
                if passive in passive_moves:
                    target_side = side_for(mon)
                    if target_side is not None:
                        source_side = "p2" if target_side == "p1" else "p1"
                        source = hazard_sources[source_side].get(passive)
                        if source is not None:
                            source.increment_passive_damage(damage)
                elif passive in passive_statuses:
                    source = status_sources.get(nickname_val)
                    if source is not None:
                        source.increment_passive_damage(damage)

            if len(parts) > 5 and "[of]" in parts[5]:
                actor = parts[5].split("[of]", 1)[1].strip()
                mon2 = _mon_for_nickname(actor)
                if mon2 is not None and damage > 0:
                    mon2.increment_passive_damage(damage)

        if line.startswith("|-heal|") or line.startswith("|-sethp|"):
            parts = line.split("|")
            mon = _mon_for_nickname(parts[2])
            if mon is not None and len(parts) > 3 and "/" in parts[3]:
                mon.set_current_hp(int(parts[3].split("/")[0]))

    return players
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

# db commands
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

def test():
    url = "https://replay.pokemonshowdown.com/gen9natdexdraft-2697965136.json"
    data = fetch_json(url)
    lines = data["log"].splitlines()

    reset()
    teams(lines)
    nickname(lines)
    _rebuild_nickname_lookup()
    passive_dmg(lines)
    for side in ("p1", "p2"):
        for mon in players[side]:
            print(f"{mon.name}: Passive Damage = {mon.get_passive_damage()}")

def main():
    test()

if __name__ == "__main__":
    main()