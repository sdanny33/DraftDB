import urllib.request
import urllib.error
import json
from mon import Mon
import sqlite3
import time
import socket

player1, player2 = "", ""
players = {
    "p1": [],
    "p2": []
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

def teams(lines):
    for line in lines:
        if line.startswith("|poke|p1|"):
            name = line.split("|poke|p1|")[1].split(",")[0].strip("|")
            players["p1"].append(Mon(name))
        elif line.startswith("|poke|p2|"):
            name = line.split("|poke|p2|")[1].split(",")[0].strip("|")
            players["p2"].append(Mon(name))

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
                    elif (players["p2"][i].name == species):
                        players["p2"][i].set_nickname(nickname)

def faint(lines):
    for line in lines:
        if line.startswith("|faint|"):
            parts = line.split("|")
            nickname = parts[2]
            for i in range(min(6, len(players["p1"]), len(players["p2"]))):
                if (players["p1"][i].nickname == nickname):
                    players["p1"][i].increment_deaths()
                elif (players["p2"][i].nickname == nickname):
                    players["p2"][i].increment_deaths()

def actors(line) -> tuple[str, str]:
    parts = line.split("|")
    nickname1 = parts[2]
    nickname2 = parts[4]
    return nickname1, nickname2

def kd(lines):
    actor1 = None
    actor2 = None
    for line in lines:
        if line.startswith("|move|"):
            actor1, actor2 = actors(line)
        if line.startswith("|faint|"):
            parts = line.split("|")
            ky = None
            if parts[2] == actor1:
                ky = actor2
            elif parts[2] == actor2:
                ky = actor1
            if ky is not None:
                for i in range(min(6, len(players["p1"]), len(players["p2"]))):
                    if (players["p1"][i].nickname == ky):
                        players["p1"][i].increment_kills()
                    elif (players["p2"][i].nickname == ky):
                        players["p2"][i].increment_kills()

def games_played():
    for i in range(min(6, len(players["p1"]), len(players["p2"]))):
        players["p1"][i].increment_games()
        players["p2"][i].increment_games()

def wins(lines):
    for line in lines:
        if line.startswith("|win|"):
            winner = line.split("|win|")[1]
            if winner == player1:
                for i in range(min(6, len(players["p1"]))):
                    players["p1"][i].increment_wins()
            elif winner == player2:
                for i in range(min(6, len(players["p2"]))):
                    players["p2"][i].increment_wins()

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
        cursor.execute('''UPDATE mons SET kills = kills + ?, deaths = deaths + ?, games_played = games_played + ?, wins = wins + ? WHERE name = ?''', (mon.kills, mon.deaths, mon.games_played, mon.wins, mon.name))

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

def reset():
    global player1, player2 
    player1, player2 = "", ""
    players["p1"] = []
    players["p2"] = []

def parse(url, dbName=None, cursor=None):
    data = fetch_json(url)
    lines = data["log"].splitlines()
    global player1, player2 
    player1, player2 = player(data)

    teams(lines)
    nickname(lines)
    faint(lines)
    kd(lines)
    wins(lines)
    games_played()
    save_to_db(dbName=dbName, cursor=cursor)
    # print_stats()
    reset()

def main():
    parse("https://replay.pokemonshowdown.com/gen9draft-2518249638.json", "testDB.sqlite")  

if __name__ == "__main__":
    main()
