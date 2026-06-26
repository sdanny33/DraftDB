import json
import socket
import urllib.request
import urllib.error
import pathlib
from mon import Mon

DB_ROOT = pathlib.Path(__file__).resolve().parent.parent

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

def _rosters_full():
    return len(players["p1"]) >= 6 and len(players["p2"]) >= 6

def _nicknames_full():
    return _rosters_full() and all(mon.nickname for mon in players["p1"][:6]) and all(mon.nickname for mon in players["p2"][:6])

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

def moves(lines):
    for line in lines:
        if line.startswith("|move|"):
            parts = line.split("|")
            nickname = parts[2]
            move = parts[3].strip("|")

            for i in range(min(6, len(players["p1"]), len(players["p2"]))):
                if (nickname != ""):
                    if (players["p1"][i].nickname == nickname and move not in players["p1"][i].moves):
                        players["p1"][i].add_moves([move])
                    elif (players["p2"][i].nickname == nickname and move not in players["p2"][i].moves):
                        players["p2"][i].add_moves([move])

def item(lines):
    for line in lines:
        if line.startswith("|-item|") or line.startswith("|-enditem|"):
            parts = line.split("|")
            nickname = parts[2]
            item = parts[3].strip("|")
            print(f"Item line: {line}, nickname: {nickname}, item: {item}")

            for i in range(min(6, len(players["p1"]), len(players["p2"]))):
                if (nickname != ""):
                    if (players["p1"][i].nickname == nickname and item != ""):
                        players["p1"][i].set_item(item)
                    elif (players["p2"][i].nickname == nickname and item != ""):
                        players["p2"][i].set_item(item)

        elif "item:" in line:
            parts = line.split("|")
            if len(parts) == 5:
                nickname = parts[2]
                item = parts[4].strip("[from] item: ")
            if len(parts) == 6:
                nickname = parts[5].strip("[of] ")
                item = parts[4].strip("[from] item: ")
            print(f"Item line: {line}, nickname: {nickname}, item: {item}")

            for i in range(min(6, len(players["p1"]), len(players["p2"]))):
                if (nickname != ""):
                    if (players["p1"][i].nickname == nickname and item != ""):
                        players["p1"][i].set_item(item)
                    elif (players["p2"][i].nickname == nickname and item != ""):
                        players["p2"][i].set_item(item)

def ability(lines):
    for line in lines:
        if line.startswith("|-ability|") or line.startswith("|-end|"):
            parts = line.split("|")
            nickname = parts[2]
            ability = parts[3].strip("|")

            for i in range(min(6, len(players["p1"]), len(players["p2"]))):
                if (nickname != ""):
                    if (players["p1"][i].nickname == nickname and ability != ""):
                        players["p1"][i].set_ability(ability)
                    elif (players["p2"][i].nickname == nickname and ability != ""):
                        players["p2"][i].set_ability(ability)

        elif "ability:" in line:
            parts = line.split("|")
            nickname = parts[2]
            ability = parts[4].strip("[from] ability: ")

            for i in range(min(6, len(players["p1"]), len(players["p2"]))):
                if (nickname != ""):
                    if (players["p1"][i].nickname == nickname and ability != ""):
                        players["p1"][i].set_ability(ability)
                    elif (players["p2"][i].nickname == nickname and ability != ""):
                        players["p2"][i].set_ability(ability)

def print_paste():
    for i in range(min(6, len(players["p1"]), len(players["p2"]))):
        players["p1"][i].print_paste()
    print("VS")
    for i in range(min(6, len(players["p1"]), len(players["p2"]))):
        players["p2"][i].print_paste()

def print_data(lines):
    print(lines)

def main():
    # url = "https://replay.pokemonshowdown.com/gen9draft-2521486668-1staiapfnxd9h1hhwskqvfbeyh9dxdwpw.json"
    url = "https://replay.pokemonshowdown.com/gen9natdexdraft-2616414331.json"
    data = fetch_json(url)
    lines = data["log"].splitlines()

    teams(lines)
    nickname(lines)
    moves(lines)
    item(lines)
    ability(lines)
    print_paste()

if __name__ == "__main__":
    main()