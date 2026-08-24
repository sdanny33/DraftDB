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

moves = {}
moves_path = DB_ROOT / "dex" / "moves.py"
if moves_path.exists():
    spec = importlib.util.spec_from_file_location("moves", str(moves_path))
    moves_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(moves_mod)
    moves = getattr(moves_mod, "moves", {})

typeChart = {}
type_chart_path = DB_ROOT / "dex" / "types.py"
if type_chart_path.exists():
    spec = importlib.util.spec_from_file_location("types", str(type_chart_path))
    type_chart_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(type_chart_mod)
    typeChart = getattr(type_chart_mod, "typeChart", {})

sets = {}
sets_path = DB_ROOT / "dex" / "gen9.py"
if sets_path.exists():
    spec = importlib.util.spec_from_file_location("gen9", str(sets_path))
    sets_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sets_mod)
    sets = getattr(sets_mod, "SETDEX_SV", {})

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

def get_evs(name, set_number=1):
    normalized_name = name

    if normalized_name in sets:
        items = list(sets[normalized_name].values())
        if set_number <= len(items):
            evs_data = items[set_number - 1].get("evs", {})
            stat_map = {
                "hp": "hp",
                "at": "atk",
                "df": "def",
                "sa": "spa",
                "sd": "spd",
                "sp": "spe",
            }
            evs_data = {stat_map.get(k, k): v for k, v in evs_data.items()}
            # print(f"Found EVs for {name} (Set {set_number}): {evs_data}")
            return {stat: int(value) for stat, value in evs_data.items()}

    return {}

def get_nature(name, set_number=1):
    normalized_name = name

    if normalized_name in sets:
        items = list(sets[normalized_name].values())
        if set_number <= len(items):
            return items[set_number - 1].get("nature", "")

    return ""

def get_item(name, set_number=1):
    normalized_name = name

    if normalized_name in sets:
        items = list(sets[normalized_name].values())
        if set_number <= len(items):
            return items[set_number - 1].get("item", "")

    return ""

def get_moves(name, set_number=1):
    normalized_name = name

    if normalized_name in sets:
        items = list(sets[normalized_name].values())
        if set_number <= len(items):
            return items[set_number - 1].get("moves", [])

    return []

def get_base_stats(name):
    normalized_name = _normalize_name(name)

    if normalized_name in dex:
        base_stats = dex[normalized_name].get("baseStats", {})
        # print(f"Found base stats for {name}: {base_stats}")
        return {stat: int(value) for stat, value in base_stats.items()}

    return {}

def get_types(name):
    normalized_name = _normalize_name(name)

    if normalized_name in dex:
        # print(f"Found types for {name}: {dex[normalized_name].get('types', [])}")
        return dex[normalized_name].get("types", [])

    return []

def get_move_base_power(name):
    normalized_name = _normalize_name(name)

    if normalized_name in moves:
        move = moves[normalized_name].get("basePower", 0)
        # print(f"Found move for {name}: {move}")
        return move

def get_move_type(name):
    normalized_name = _normalize_name(name)

    if normalized_name in moves:
        move_type = moves[normalized_name].get("type", "")
        # print(f"Found move type for {name}: {move_type}")
        return move_type

def get_move_category(name):
    normalized_name = _normalize_name(name)

    if normalized_name in moves:
        move_category = moves[normalized_name].get("category", "")
        # print(f"Found move category for {name}: {move_category}")
        return move_category

def get_type_chart():
    return typeChart

def get_nature_modifiers(nature):
    """Returns a dictionary of stat modifiers based on the Pokémon's nature."""
    nature_modifiers = {
        "adamant": {"atk": 1.1, "spa": 0.9},
        "bashful": {},
        "bold": {"def": 1.1, "atk": 0.9},
        "brave": {"atk": 1.1, "spe": 0.9},
        "calm": {"spd": 1.1, "atk": 0.9},
        "careful": {"spd": 1.1, "spa": 0.9},
        "docile": {},
        "gentle": {"spd": 1.1, "def": 0.9},
        "hardy": {},
        "hasty": {"spe": 1.1, "def": 0.9},
        "impish": {"def": 1.1, "spa": 0.9},
        "jolly": {"spe": 1.1, "spa": 0.9},
        "lax": {"def": 1.1, "spd": 0.9},
        "lonely": {"atk": 1.1, "def": 0.9},
        "mild": {"spa": 1.1, "def": 0.9},
        "modest": {"spa": 1.1, "atk": 0.9},
        "naive": {"spe": 1.1, "spd": 0.9},
        "naughty": {"atk": 1.1, "spd": 0.9},
        "quiet": {"spa": 1.1, "spe": 0.9},
        "quirky": {},
        "rash": {"spa": 1.1, "spd": 0.9},
        "relaxed": {"def": 1.1, "spe": 0.9},
        "sassy": {"spd": 1.1, "spe": 0.9},
        "serious": {},
        "timid": {"spe": 1.1, "atk": 0.9}
    }
    return nature_modifiers.get(nature.lower(), {})

def get_forme_name(name):
    normalized_name = _normalize_name(name)

    if normalized_name in dex:
        forme_name = dex[normalized_name].get("otherFormes", [])
        # print(f"Found forme name for {name}: {forme_name}")
        return forme_name

    return []

def get_base_species(name):
    normalized_name = _normalize_name(name)

    if normalized_name in dex:
        base_species = dex[normalized_name].get("baseSpecies", "")
        # print(f"Found base species for {name}: {base_species}")
        return base_species

    return ""

def get_set_count(name: str) -> int:
    """Returns the total number of sets available for a given Pokemon."""
    if name in sets:
        return len(sets[name])
    return 0

def main():
    # Example usage
    get_nature("Pecharunt", 2)

if __name__ == "__main__":
    main()