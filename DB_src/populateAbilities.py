from pathlib import Path
import re
from parser import fetch_json, teams

DB_ROOT = Path(__file__).resolve().parent.parent

players = {
    "p1": [],
    "p2": []
}

def _normalize_name(name):
    return re.sub(r"[^a-z0-9]", "", name.lower())

def get_abilities(name):
    file = DB_ROOT / "dex" / "pokedex.ts"
    text = file.read_text()
    normalized_name = _normalize_name(name)

    pattern = re.compile(
        r'name:\s*"(?P<name>[^"]+)".*?abilities:\s*\{(?P<abilities>.*?)\}',
        re.DOTALL,
    )

    for match in pattern.finditer(text):
        if _normalize_name(match.group("name")) != normalized_name:
            continue

        abilities = re.findall(r':\s*"([^"]+)"', match.group("abilities"))
        return abilities

    return []

def populate_abilities(team1, team2):
    for i in range(min(6, len(team1), len(team2))):
        if team1[i].name:
            abilities = get_abilities(team1[i].name)
            if abilities:
                team1[i].set_ability(" / ".join(abilities))
        if team2[i].name:
            abilities = get_abilities(team2[i].name)
            if abilities:
                team2[i].set_ability(" / ".join(abilities))

def get_evs(name):
    file = DB_ROOT / "dex" / "gen9.js"
    text = file.read_text()
    normalized_name = _normalize_name(name)

    pattern = re.compile(
        r'"(?P<name>[^"]+)":\s*\{(?P<movesets>.*?\}\s*(?:,\s*"[^"]+":\s*\{|\}\s*,|\}\s*$))',
        re.DOTALL,
    )

    for match in pattern.finditer(text):
        if _normalize_name(match.group("name")) != normalized_name:
            continue

        movesets = match.group("movesets")
        evs_match = re.search(r'"evs":\{([^}]+)\}', movesets)
        if evs_match:
            evs_str = evs_match.group(1)
            evs_dict = {"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0}
            stat_map = {
                "hp": "hp",
                "at": "atk",
                "df": "def",
                "sa": "spa",
                "sd": "spd",
                "sp": "spe",
            }
            for stat_key, value in re.findall(r'"([a-z]+)":(\d+)', evs_str):
                if stat_key in stat_map:
                    evs_dict[stat_map[stat_key]] = int(value)
            return evs_dict

    return {"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0}

def populate_evs(team1, team2):
    for i in range(min(6, len(team1), len(team2))):
        if team1[i].name:
            evs = get_evs(team1[i].name)
            if any(evs.values()):
                team1[i].set_evs(evs)
        if team2[i].name:
            evs = get_evs(team2[i].name)
            if any(evs.values()):
                team2[i].set_evs(evs)

def get_nature(name):
    file = DB_ROOT / "dex" / "gen9.js"
    text = file.read_text()
    normalized_name = _normalize_name(name)

    pattern = re.compile(
        r'"(?P<name>[^"]+)":\s*\{(?P<movesets>.*?\}\s*(?:,\s*"[^"]+":\s*\{|\}\s*,|\}\s*$))',
        re.DOTALL,
    )

    for match in pattern.finditer(text):
        if _normalize_name(match.group("name")) != normalized_name:
            continue

        movesets = match.group("movesets")
        nature_match = re.search(r'"nature":"([^"]+)"', movesets)
        if nature_match:
            return nature_match.group(1)

    return ""

def populate_nature(team1, team2):
    for i in range(min(6, len(team1), len(team2))):
        if team1[i].name:
            nature = get_nature(team1[i].name)
            if nature:
                team1[i].set_nature(nature)
        if team2[i].name:
            nature = get_nature(team2[i].name)
            if nature:
                team2[i].set_nature(nature)

def get_base_stats(name):
    file = DB_ROOT / "dex" / "pokedex.ts"
    text = file.read_text()
    normalized_name = _normalize_name(name)

    pattern = re.compile(
        r'name:\s*"(?P<name>[^"]+)".*?baseStats:\s*\{(?P<baseStats>.*?)\}',
        re.DOTALL,
    )

    for match in pattern.finditer(text):
        if _normalize_name(match.group("name")) != normalized_name:
            continue

        stats_block = match.group("baseStats")
        stat_pairs = re.findall(r'([a-z]+)\s*:\s*(\d+)', stats_block)
        if stat_pairs:
            return {stat: int(value) for stat, value in stat_pairs}

    return {}

def populate_base_stats(team1, team2):
    for i in range(min(6, len(team1), len(team2))):
        if team1[i].name:
            base_stats = get_base_stats(team1[i].name)
            if base_stats:
                team1[i].set_base_stats(base_stats)
        if team2[i].name:
            base_stats = get_base_stats(team2[i].name)
            if base_stats:
                team2[i].set_base_stats(base_stats)

def public_ability(lines, file):
    for line in lines:
        if line.startswith("|-ability|"):
            parts = line.split("|")
            ability = parts[3].strip("|")

            with open(file, "a") as f:
                f.seek(0)
                if ability not in f.read():
                    f.write(f"{ability}\n")
                    print(f"Added ability: {ability}")

def get_public_abilities(input_file, output_file):
        with open(input_file, 'r') as f:
            for raw in f:
                url = raw.strip()
                data = fetch_json(url)
                lines = data["log"].splitlines()
                public_ability(lines, output_file)

def main():
    # Example usage
    url = "https://replay.pokemonshowdown.com/gen9natdexdraft-2616414331.json"
    data = fetch_json(url)
    lines = data["log"].splitlines()

    teams(lines)
    get_base_stats("Pikachu")

if __name__ == "__main__":
    main()