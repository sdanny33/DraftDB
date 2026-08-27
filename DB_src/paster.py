import pathlib
from mon import Mon
from parser import fetch_json, teams, nickname, players
import populateInfo

DB_ROOT = pathlib.Path(__file__).resolve().parent.parent
nickname_lookup = {
    "p1": {},
    "p2": {}
}

def _remove_prefix(value, prefix):
    if value.startswith(prefix):
        return value[len(prefix):]
    return value

def _extract_slot(parts):
    for part in parts:
        cleaned = _remove_prefix(part, "[of] ").strip()
        if cleaned.startswith(("p1", "p2")):
            return cleaned.split(",", 1)[0].strip()
    return ""

def _extract_source(parts, prefix):
    for part in parts:
        if part.startswith(prefix):
            return _remove_prefix(part, prefix)
    return ""

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

def apply_mega_evolution(mon: Mon, raw_species: str, item: str = ""):
    """Updates the Mon instance with Mega stats, types, ability, and name."""
    mega_species = raw_species
    if item.endswith("ite X") or item.endswith("ite Y"):
        forme_suffix = item.split()[-1]
        mega_species = f"{raw_species}-Mega-{forme_suffix}"
    elif item.endswith("ite") or "Mega" not in mega_species:
        if not mega_species.endswith("-Mega"):
            mega_species = f"{raw_species}-Mega"

    if not populateInfo.get_base_stats(mega_species):
        if populateInfo.get_base_stats(raw_species):
            mega_species = raw_species

    mon.set_name(mega_species)
    mon.set_base_stats(populateInfo.get_base_stats(mega_species))
    mon.set_type(populateInfo.get_types(mega_species))
    
    mega_abilities = populateInfo.get_abilities(mega_species)
    if mega_abilities:
        mon.set_ability(mega_abilities)

def moves(lines):
    for line in lines:
        if line.startswith("|move|"):
            parts = line.split("|")
            nickname = parts[2]
            move = parts[3].strip("|")
            mon = _mon_for_nickname(nickname)
            if mon is not None and move not in mon.moves:
                mon.add_moves([move])

def item(lines):
    for line in lines:
        if line.startswith("|-item|") or line.startswith("|-enditem|"):
            parts = line.split("|")
            nickname = parts[2]
            item = parts[3].strip("|")
            #print(f"Item line: {line}, nickname: {nickname}, item: {item}")
            mon = _mon_for_nickname(nickname)
            if mon is not None and item != "":
                mon.set_item(item)

        elif "item:" in line:
            parts = line.split("|")
            if line.startswith("|-damage|") and len(parts) > 5:
                # print(f"Damage line: {parts}")
                nickname = parts[5].strip("[of] ")
                item = _extract_source(parts, "[from] item: ")
            else:
                nickname = _extract_slot(parts)
                item = _extract_source(parts, "[from] item: ")
            # print(f"Item line: {line}, nickname: {nickname}, item: {item}")
            mon = _mon_for_nickname(nickname)
            if mon is not None and item != "":
                mon.set_item(item)

        elif line.startswith("|-mega|"):
            parts = line.split("|")
            nickname_val = parts[2]
            raw_species = parts[3].strip()
            item = parts[4].strip() if len(parts) > 4 else ""
            
            mon = _mon_for_nickname(nickname_val)
            if mon is not None and item != "":
                mon.set_item(item)
            if mon:
                apply_mega_evolution(mon, raw_species, item)

def ability(lines):
    for line in lines:
        if line.startswith("|-ability|"):
            parts = line.split("|")
            nickname = parts[2]
            ability = parts[3].strip("|")
            # print(f"Ability line: {line}, nickname: {nickname}, ability: {ability}")
            mon = _mon_for_nickname(nickname)
            if mon is not None and ability != "":
                mon.set_ability(ability)

        elif "ability:" in line:
            parts = line.split("|")
            nickname = _extract_slot(parts)
            ability = _extract_source(parts, "[from] ability: ")
            # print(f"Ability line: {line}, nickname: {nickname}, ability: {ability}")
            mon = _mon_for_nickname(nickname)
            if mon is not None and ability != "":
                mon.set_ability(ability)

def print_clear():
    for i in range(min(6, len(players["p1"]), len(players["p2"]))):
        players["p1"][i].print_clear()
    print("VS")
    for i in range(min(6, len(players["p1"]), len(players["p2"]))):
        players["p2"][i].print_clear()

def print_paste():
    for i in range(min(6, len(players["p1"]), len(players["p2"]))):
        players["p1"][i].print_paste()
    print("VS")
    for i in range(min(6, len(players["p1"]), len(players["p2"]))):
        players["p2"][i].print_paste()

def print_data(lines):
    print(lines)

def main():
    url = "https://replay.pokemonshowdown.com/gen9natdexdraft-2644608154.json"
    data = fetch_json(url)
    lines = data["log"].splitlines()

    teams(lines)
    nickname(lines)
    _rebuild_nickname_lookup()
    moves(lines)
    item(lines)
    ability(lines)
    print_paste()

if __name__ == "__main__":
    main()