from pathlib import Path
import re
from pokedex import get_dex
from moves import get_moves
from mtypes import get_type_chart
from gen9 import get_sets

dex = get_dex()  # Retrieve the dex dictionary from pokedex.py
moves = get_moves()  # Retrieve the moves dictionary from moves.py
typeChart = get_type_chart()  # Retrieve the typeChart dictionary from mtypes.py
sets = get_sets()  # Retrieve the sets dictionary from gen9.py

def _normalize_name(name):
    new_name = re.sub(r"[^a-z0-9]", "", name.lower())
    new_name = re.sub(r"-", "", new_name)
    new_name = re.sub(r" ", "", new_name)
    # print(new_name)
    return new_name

def generate_basic_sets(name: str) -> list[dict]:
    """Generates standard baseline sets tailored to the Pokemon's base stats."""
    base = get_base_stats(name)
    if not base:
        return []

    # Determine offensive preference
    is_physical = base.get("atk", 0) >= base.get("spa", 0)
    atk_stat = "at" if is_physical else "sa"
    speed_nature = "Jolly" if is_physical else "Timid"
    boost_nature = "Adamant" if is_physical else "Modest"
    choice_item = "Choice Band" if is_physical else "Choice Specs"

    # Determine defensive natures
    def_nature = "Impish" if is_physical else "Bold"
    spd_nature = "Careful" if is_physical else "Calm"

    sets_list = [
        # 1. 252 Atk/SpA / 252 Spe / 4 HP (+Spe)
        {"nature": speed_nature, "evs": {atk_stat: 252, "sp": 252, "hp": 4}, "item": "Leftovers"},
        # 2. 252 Atk/SpA / 252 Spe / 4 HP (+Atk/SpA)
        {"nature": boost_nature, "evs": {atk_stat: 252, "sp": 252, "hp": 4}, "item": "Leftovers"},
        # 3. 252 Atk/SpA / 252 Spe / 4 HP (+Spe, Choice)
        {"nature": speed_nature, "evs": {atk_stat: 252, "sp": 252, "hp": 4}, "item": choice_item},
        # 4. 252 Atk/SpA / 252 Spe / 4 HP (+Atk/SpA, Choice)
        {"nature": boost_nature, "evs": {atk_stat: 252, "sp": 252, "hp": 4}, "item": choice_item},
        # 5. 128 Atk/SpA / 252 Spe / 128 HP (+Spe)
        {"nature": speed_nature, "evs": {atk_stat: 128, "sp": 252, "hp": 128}, "item": "Leftovers"},
        # 6. 252 Atk/SpA / 252 HP / 4 Spe (+Atk/SpA)
        {"nature": boost_nature, "evs": {atk_stat: 252, "hp": 252, "sp": 4}, "item": "Leftovers"},
        # 7. 252 Atk/SpA / 252 Spe / 4 HP (+Spe, Choice Scarf)
        {"nature": speed_nature, "evs": {atk_stat: 252, "sp": 252, "hp": 4}, "item": "Choice Scarf"},
        # 8. 252 Def / 252 HP / 4 Spe (+Def)
        {"nature": def_nature, "evs": {"df": 252, "hp": 252, "sp": 4}, "item": "Leftovers"},
        # 9. 252 SpD / 252 HP / 4 Spe (+SpD)
        {"nature": spd_nature, "evs": {"sd": 252, "hp": 252, "sp": 4}, "item": "Leftovers"},
        # 10. 252 SpD / 252 HP / 4 Spe (+SpD, Assault Vest)
        {"nature": spd_nature, "evs": {"sd": 252, "hp": 252, "sp": 4}, "item": "Assault Vest"},
        # 11. 128 SpD / 252 HP / 128 Def (+SpD)
        {"nature": spd_nature, "evs": {"sd": 128, "hp": 252, "df": 128}, "item": "Leftovers"},
        # 12. 128 Def / 252 HP / 128 SpD (+Def)
        {"nature": def_nature, "evs": {"df": 128, "hp": 252, "sd": 128}, "item": "Leftovers"},
    ]

    return sets_list

def get_abilities(name):
    normalized_name = _normalize_name(name)

    if normalized_name in dex:
        abilities = dex[normalized_name].get("abilities", {})
        if len(abilities) == 1:
            return abilities.get("0", "")
        return [ability for ability in abilities.values() if ability]

    return []

def get_all_sets_for_mon(name: str) -> list[dict]:
    """Combines basic sets first with custom Smogon tier sets second."""
    basic_sets = generate_basic_sets(name)
    custom_sets = list(sets[name].values()) if name in sets else []
    return basic_sets + custom_sets

def get_set_count(name: str) -> int:
    """Returns the total number of basic + custom sets."""
    return len(get_all_sets_for_mon(name))

def get_evs(name: str, set_number: int = 1) -> dict:
    all_sets = get_all_sets_for_mon(name)
    if 1 <= set_number <= len(all_sets):
        evs_data = all_sets[set_number - 1].get("evs", {})
        stat_map = {
            "hp": "hp",
            "at": "atk",
            "df": "def",
            "sa": "spa",
            "sd": "spd",
            "sp": "spe",
        }
        return {stat_map.get(k, k): int(v) for k, v in evs_data.items()}
    return {}

def get_nature(name: str, set_number: int = 1) -> str:
    all_sets = get_all_sets_for_mon(name)
    if 1 <= set_number <= len(all_sets):
        return all_sets[set_number - 1].get("nature", "")
    return ""

def get_item(name: str, set_number: int = 1) -> str:
    all_sets = get_all_sets_for_mon(name)
    if 1 <= set_number <= len(all_sets):
        return all_sets[set_number - 1].get("item", "")
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

def get_types(name) -> list[str]:
    normalized_name = _normalize_name(name)

    if normalized_name in dex:
        # print(f"Found types for {name}: {dex[normalized_name].get('types', [])}")
        return dex[normalized_name].get("types", [])

    return []

def get_move_base_power(name) -> int:
    normalized_name = _normalize_name(name)

    if normalized_name in moves:
        move = moves[normalized_name].get("basePower", 0)
        # print(f"Found move for {name}: {move}")
        return move
    return 0

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

def main():
    # Example usage
    get_abilities("Landorus-Therian")
    get_abilities("Garchomp")

if __name__ == "__main__":
    main()