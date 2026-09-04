import urllib.request
import urllib.error
import json
from mon import Mon
import sqlite3
import socket
from pathlib import Path

DB_ROOT = Path(__file__).resolve().parent.parent

player1, player2 = "", ""
players = {
    "p1": [],
    "p2": []
}
nickname_lookup = {
    "p1": {},
    "p2": {}
}

def _is_timeout_error(error):
    if isinstance(error, (TimeoutError, socket.timeout)):
        return True

    if isinstance(error, urllib.error.URLError):
        reason = error.reason
        if isinstance(reason, (TimeoutError, socket.timeout)):
            return True
        if isinstance(reason, str) and "timed out" in reason.lower():
            return True

    return False

def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as response:
        html = response.read().decode('utf-8')
        data = json.loads(html)
        return data

    if last_error is not None and _is_timeout_error(last_error):
        raise TimeoutError(f"Replay fetch timed out for {url}") from last_error

    raise RuntimeError(f"Failed to fetch replay JSON from {url}") from last_error

def _rosters_full():
    return len(players["p1"]) >= 6 and len(players["p2"]) >= 6

def _nicknames_full():
    return _rosters_full() and all(mon.nickname for mon in players["p1"][:6]) and all(mon.nickname for mon in players["p2"][:6])

def _clear_nickname_lookup():
    nickname_lookup["p1"].clear()
    nickname_lookup["p2"].clear()

def _rebuild_nickname_lookup():
    _clear_nickname_lookup()
    for side in ("p1", "p2"):
        for mon in players[side]:
            if mon.nickname:
                nickname_lookup[side][mon.nickname] = mon

def _mon_for_nickname(nickname):
    mon = nickname_lookup["p1"].get(nickname)
    if mon is not None:
        return mon
    return nickname_lookup["p2"].get(nickname)

def teams(lines):
    for line in lines:
        if line.startswith("|poke|p1|"):
            name = line.split("|poke|p1|")[1].split(",")[0].strip("|")
            if (name.endswith("-*")):
                name = name[:-2]
            players["p1"].append(Mon(name))
        elif line.startswith("|poke|p2|"):
            name = line.split("|poke|p2|")[1].split(",")[0].strip("|")
            if (name.endswith("-*")):
                name = name[:-2]
            players["p2"].append(Mon(name))

        if _rosters_full():
            break

def nickname(lines):
    for line in lines:
        if line.startswith("|switch|"):
            parts = line.split("|")
            nickname = parts[2]
            species = parts[3].split(",")[0].strip("|")

            for i in range(min(6, len(players["p1"]), len(players["p2"]))):
                if (nickname != ""):
                    if (players["p1"][i].name == species):
                        players["p1"][i].set_nickname(nickname)
                    # urshifu clause
                    elif (players["p1"][i].name == "Urshifu" and species == "Urshifu-Rapid-Strike"):
                        players["p1"][i].set_name(species)
                        players["p1"][i].set_nickname(nickname)
                    elif (players["p2"][i].name == species):
                        players["p2"][i].set_nickname(nickname)
                    # urshifu clause
                    elif (players["p2"][i].name == "Urshifu" and species == "Urshifu-Rapid-Strike"):
                        players["p2"][i].set_name(species)
                        players["p2"][i].set_nickname(nickname)

            if _nicknames_full():
                break

def actors(line) -> tuple[str, str]:
    parts = line.split("|")
    nickname1 = parts[2]
    nickname2 = parts[4]
    return nickname1, nickname2

def battle_stats(lines):
    actor1 = None
    actor2 = None
    move = None
    for line in lines:
        if line.startswith("|move|"):
            actor1, actor2 = actors(line)
            move = line.split("|")[3]

        if line.startswith("|faint|"):
            parts = line.split("|")
            nickname = parts[2]
            mon = _mon_for_nickname(nickname)
            if mon is not None:
                mon.increment_deaths()

            ky = None
            if nickname == actor1:
                ky = actor2
            elif nickname == actor2:
                ky = actor1

            if ky is not None:
                mon = _mon_for_nickname(ky)
                if mon is not None:
                    mon.increment_kills()

        if line.startswith("|-damage|"):
            parts = line.split("|")
            nickname = parts[2]
            hp_str = parts[3]

            is_passive = any("[from]" in p for p in parts[4:])

            mon1 = _mon_for_nickname(nickname) # The defender/victim
            mon2 = None                         # The attacker
            if actor1 is not None and not is_passive:
                # actor1 is always the Pokemon that executed the move
                mon2 = _mon_for_nickname(actor1)

            if mon1 is not None:
                current_hp = 0 if "fnt" in hp_str else int(hp_str.split("/")[0])
                damage = mon1.get_current_hp() - current_hp
                mon1.set_current_hp(current_hp)
                
                if damage > 0:
                    mon1.increment_damage_taken(damage)
                    if mon2 is not None and mon1 != mon2:
                        mon2.increment_damage(damage)
                        print(f"{mon2.name} dealt {damage} damage to {mon1.name} (current HP: {current_hp})")

        if line.startswith("|-heal|") or line.startswith("|-sethp|"):
            parts = line.split("|")
            nickname_val = parts[2]
            mon = _mon_for_nickname(nickname_val)

            if mon is not None and len(parts) > 3 and "/" in parts[3]:
                new_hp = int(parts[3].split("/")[0])
                diff = new_hp - mon.get_current_hp()
                mon.set_current_hp(new_hp)

                if diff > 0:
                    mon.increment_heal(diff)
                    print(f"{mon.name} healed {diff} HP (current HP: {new_hp})")
                elif diff < 0:
                    # Handles HP drops caused by |-sethp| (e.g., Pain Split)
                    mon.increment_damage_taken(-diff)

        if line.startswith("|win|"):
            winner = line.split("|win|")[1]
            if winner == player1:
                for i in range(min(6, len(players["p1"]))):
                    players["p1"][i].increment_wins()
            elif winner == player2:
                for i in range(min(6, len(players["p2"]))):
                    players["p2"][i].increment_wins()

def games_played():
    for i in range(min(6, len(players["p1"]), len(players["p2"]))):
        players["p1"][i].increment_games()
        players["p2"][i].increment_games()

def mega_evolutions(lines):
    for line in lines:
        if line.startswith("|detailschange|"):
            parts = line.split("|")
            nickname = parts[2]
            new_species = parts[3].split(",")[0].strip("|")
            mon = _mon_for_nickname(nickname)
            original_species = mon.name if mon is not None else None
            if mon is not None:
                mon.set_name(new_species)

def print_stats():
    print(f"Player 1: {player1}")
    for i in range(min(6, len(players["p1"]))):
        players["p1"][i].print_stats()
    print()
    print(f"Player 2: {player2}")
    for i in range(min(6, len(players["p2"]))):
        players["p2"][i].print_stats()
    print()

def save_to_db(dbName=None, cursor=None):
    own_connection = False
    if cursor is None:
        if dbName is None:
            raise ValueError("dbName is required when cursor is not provided")
        conn = sqlite3.connect(dbName)
        cursor = conn.cursor()
        own_connection = True

    def add_mon_stats(mon):
        cursor.execute('''UPDATE mons SET kills = kills + ?, deaths = deaths + ?, games_played = games_played + ?, wins = wins + ?, damage = damage + ?, healing = healing + ? WHERE name = ?''', (mon.kills, mon.deaths, mon.games_played, mon.wins, mon.damage, mon.healing, mon.name))

    for i in range(min(6, len(players["p1"]), len(players["p2"]))):
        add_mon_stats(players["p1"][i])
        add_mon_stats(players["p2"][i])
    
    if own_connection:
        conn.commit()
        conn.close()

def player(data):
    player1 = data["players"][0]
    player2 = data["players"][1]
    return player1, player2

def player_lines(lines):
    player1, player2 = "", ""
    for line in lines:
        if line.startswith("|player|p1|"):
            player1 = line.split("|player|p1|")[1].split("|")[0]
        elif line.startswith("|player|p2|"):
            player2 = line.split("|player|p2|")[1].split("|")[0]
    return player1, player2

def reset():
    global player1, player2 
    player1, player2 = "", ""
    players["p1"] = []
    players["p2"] = []
    _clear_nickname_lookup()

def parse(url, dbName=None, cursor=None):
    data = fetch_json(url)
    lines = data["log"].splitlines()
    global player1, player2 
    player1, player2 = player(data)
    try:
        teams(lines)
        nickname(lines)
        _rebuild_nickname_lookup()
        mega_evolutions(lines)
        battle_stats(lines)
        games_played()
        save_to_db(dbName=dbName, cursor=cursor)
    finally:
        reset()

def parse_lines(lines, dbName=None, cursor=None):
    global player1, player2 
    player1, player2 = player_lines(lines)
    try:
        teams(lines)
        nickname(lines)
        _rebuild_nickname_lookup()
        mega_evolutions(lines)
        battle_stats(lines)
        games_played()
        save_to_db(dbName=dbName, cursor=cursor)
    finally:
        reset()

def test():
    url = "https://replay.pokemonshowdown.com/gen9natdexdraft-2675562822.json"
    data = fetch_json(url)
    lines = data["log"].splitlines()
    global player1, player2 
    player1, player2 = player(data)

    teams(lines)
    nickname(lines)
    _rebuild_nickname_lookup()
    mega_evolutions(lines)
    battle_stats(lines)
    games_played()
    print_stats()

def main():
    replay_csv_path = DB_ROOT / 'DB_CSV' / 'replaysDraft.csv'
    archive_csv_path = DB_ROOT / 'DB_CSV' / 'replaysReDraft.csv'
    test()

if __name__ == "__main__":
    main()
