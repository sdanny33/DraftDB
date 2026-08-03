from pathlib import Path
import re
import importlib.util

DB_ROOT = Path(__file__).resolve().parent.parent

dex = {}
pokedex_path = DB_ROOT / "dex" / "pokedex.py"
if pokedex_path.exists():
    spec = importlib.util.spec_from_file_location("pokedex", str(pokedex_path))
    pokedex_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pokedex_mod)
    dex = getattr(pokedex_mod, "dex", {})

def _normalize_name(name):
    new_name = re.sub(r"[^a-z0-9]", "", name.lower())
    new_name = re.sub(r"-", "", new_name)
    new_name = re.sub(r" ", "", new_name)
    # print(new_name)
    return new_name

def get_abilities(name):
    normalized_name = _normalize_name(name)

    if normalized_name in dex:
        abilities = dex[normalized_name].get("abilities", {})
        # print(f"Found abilities for {name}: {abilities}")
        return [ability for ability in abilities.values() if ability]

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
    normalized_name = _normalize_name(name)

    if normalized_name in dex:
        base_stats = dex[normalized_name].get("baseStats", {})
        # print(f"Found base stats for {name}: {base_stats}")
        return {stat: int(value) for stat, value in base_stats.items()}

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


def get_types(name):
    normalized_name = _normalize_name(name)

    if normalized_name in dex:
        # print(f"Found types for {name}: {dex[normalized_name].get('types', [])}")
        return dex[normalized_name].get("types", [])

    return []

def populate_types(team1, team2):
    for i in range(min(6, len(team1), len(team2))):
        if team1[i].name:
            types = get_types(team1[i].name)
            if types:
                team1[i].set_type(types)
        if team2[i].name:
            types = get_types(team2[i].name)
            if types:
                team2[i].set_type(types)

def main():
    # Example usage
    get_types("Pikachu")

if __name__ == "__main__":
    main()