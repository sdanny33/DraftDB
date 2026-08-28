import sys
from pathlib import Path

# Add DB_src directory to Python module search path
SRC_DIR = Path(__file__).resolve().parent.parent / "DB_src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
from mon import Mon
from parser import _mon_for_nickname, _rebuild_nickname_lookup, fetch_json, actors, teams, nickname, players
from paster import print_paste

import re
from bs4 import BeautifulSoup
import requests
import math
from populateInfo import *
from items import get_item_stat_multiplier, get_item_power_multiplier
from abilities import get_ability_stat_multiplier, get_ability_power_multiplier, get_ability_stab_multiplier, get_ability_damage_multiplier, get_effective_move_type

def extract(url):
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        all_pre = soup.find_all('pre')
        for pre in all_pre:
            extract = pre.get_text()

            replacements = [
                (r'Shiny: Yes  ', ''),
                (r'IVs: .*', ''),
                (r'\((F)\) ', ''),
                (r'\((M)\) ', '')
            ]
            for pattern, replacement in replacements:
                extract = re.sub(pattern, replacement, extract)

            lines = [line for line in extract.splitlines() if line.strip()]
            if not lines:
                continue
            
            def replace_parenthetical(line):
                m = re.match(r'.*\(([^)]*)\)\s*(.*)', line)
                if m:
                    name = m.group(1).strip()
                    rest = m.group(2).strip()
                    return f"{name} {rest}".strip()
                return line

            lines = [replace_parenthetical(line) for line in lines]

            clean_extract = '\n'.join(lines) + '\n'
            extract = clean_extract
            set_mon_data(extract)

def set_mon_data(info):
    mon_data = info.splitlines()
    name = mon_data[0].split(" @ ")[0]
    formes = get_base_species(name)
    
    # Find the corresponding Mon object in players
    m = None
    index = min(6, len(players["p1"]), len(players["p2"]))
    for i in range(index):
        if players["p1"][i].name in (name, formes):
            players["p1"][i].set_name(name)
            m = players["p1"][i]
            break
        elif players["p2"][i].name in (name, formes):
            players["p2"][i].set_name(name)
            m = players["p2"][i]
            break

    if m is None:
        return

    # Lock this Mon so try_find_matching_sets keeps it static
    m.is_extracted = True
    m.set_item(mon_data[0].split(" @ ")[1])
    m.set_ability(mon_data[1].removeprefix("Ability: "))
    
    nature_idx = find_index(mon_data, " Nature")
    if nature_idx != -1:
        m.set_nature(mon_data[nature_idx].split(" Nature")[0])
        
    m.reset_evs()
    evs_idx = find_index(mon_data, "EVs: ")
    if evs_idx != -1:
        evs_line = mon_data[evs_idx].removeprefix("EVs: ").split("/")
        evs_values = [ev.strip() for ev in evs_line]
        for ev in evs_values:
            ev_value = int(ev.split(" ")[0])
            ev_stat = ev.split(" ")[1]
            m.evs[ev_stat.lower()] = ev_value
            
    # moves
    move_index = find_index(mon_data, "- ")
    if move_index != -1:
        for offset in range(4):
            if index_exists(mon_data, move_index + offset) and mon_data[move_index + offset].startswith("- "):
                m.add_moves([mon_data[move_index + offset].strip().removeprefix("- ").strip()])

def find_index(mon_data, search_string):
    for i, line in enumerate(mon_data):
        if search_string in line:
            return i
    return -1

def index_exists(mon_data, move_index):
    return move_index < len(mon_data) and move_index >= 0

# --- Stat & Damage Calculations ---

def calculate_stat(mon: Mon, stat_name: str, is_critical: bool = False, is_attacker: bool = True) -> int:
    base_stat = mon.get_base_stats()[stat_name]
    ev_stat = mon.get_evs()[stat_name]
    level = mon.get_level()
    boosts = mon.get_boosts()

    stat_value = math.floor((math.floor(((2 * base_stat + 31 + math.floor(ev_stat / 4)) * level) / 100) + 5) * calculate_nature_modifiers(mon, stat_name))
    
    if stat_name in boosts:
        boost_stage = boosts[stat_name]
        apply_boost = True
        if is_critical:
            if is_attacker and boost_stage < 0:
                apply_boost = False
            elif not is_attacker and boost_stage > 0:
                apply_boost = False

        if apply_boost:
            if boost_stage > 0:
                stat_value = math.floor(stat_value * (1 + 0.5 * boost_stage))
            elif boost_stage < 0:
                stat_value = math.floor(stat_value * (2 / (2 - boost_stage)))

    # Item & Ability Multipliers
    stat_value = math.floor(stat_value * get_item_stat_multiplier(mon.get_item(), stat_name))
    stat_value = math.floor(stat_value * get_ability_stat_multiplier(mon.get_ability(), stat_name, mon.get_item(), mon.get_current_hp()))
    
    return stat_value

def calculate_damage(
    move_power: int,
    attack_stat: int,
    defense_stat: int,
    attacker_level: int = 100,
    targets: int = 1,
    weather_multiplier: float = 1.0,
    is_critical: bool = False,
    stab: float = 1.0,
    type_effectiveness: float = 1.0,
    burn_multiplier: float = 1.0,
) -> list[int]:
    """Calculates all 16 possible damage roll outcomes."""
    if move_power == 0 or defense_stat == 0:
        return [0]

    level_factor = math.floor((2 * attacker_level) / 5) + 2
    base_damage = math.floor(
        math.floor((level_factor * move_power * (attack_stat / defense_stat))) / 50
    ) + 2

    modifier = 1.0
    if targets > 1:
        modifier *= 0.75
    if weather_multiplier != 1.0:
        modifier *= weather_multiplier
    if is_critical:
        modifier *= 1.5
    
    modifier *= stab * type_effectiveness * burn_multiplier

    damage_rolls = []
    for roll in range(85, 101):
        final_damage = math.floor(base_damage * (roll / 100.0) * modifier)
        damage_rolls.append(max(1, final_damage))

    return damage_rolls

def calcuate_hp(mon: Mon) -> int:
    """Calculates the max HP of a Pokémon."""
    base_hp = mon.get_base_stats()["hp"]
    ev_hp = mon.get_evs()["hp"]
    level = mon.get_level()
    return math.floor(((2 * base_hp + 31 + math.floor(ev_hp / 4)) * level) / 100) + level + 10

def calculate_nature_modifiers(mon: Mon, stat_name: str) -> float:
    nature = mon.get_nature()
    if not nature:
        return 1.0
    modifiers = get_nature_modifiers(nature)
    return modifiers.get(stat_name, 1.0)

def get_type_effectiveness(move_type: str, target_types: list[str]) -> float:
    type_chart = get_type_chart()
    effectiveness = 1.0
    for target_type in target_types:
        if move_type in type_chart and target_type in type_chart[move_type]:
            effectiveness *= type_chart[move_type][target_type]
    return effectiveness

def get_category(move_name: str) -> str:
    category = get_move_category(move_name)
    return "atk" if category == "Physical" else "spa"

def get_defense_category(move_name: str) -> str:
    category = get_move_category(move_name)
    return "def" if category == "Physical" else "spd"

# --- Simulation & Set Optimization ---

def simulate_hit(actor1: Mon, actor2: Mon, move: str, is_critical: bool = False) -> tuple[int, int]:
    raw_move_type = get_move_type(move)
    move_type = get_effective_move_type(actor1.get_ability(), raw_move_type)
    base_power = get_move_base_power(move)
    
    # Offensive Base Power Modifiers (Item + Ability)
    power_mult = get_item_power_multiplier(actor1.get_item(), move_type) * get_ability_power_multiplier(
        actor1.get_ability(), move_type, base_power, actor1.get_current_hp()
    )
    modified_power = math.floor(base_power * power_mult)
    
    attack_stat = calculate_stat(actor1, get_category(move), is_critical=is_critical, is_attacker=True)
    defense_stat = calculate_stat(actor2, get_defense_category(move), is_critical=is_critical, is_attacker=False)

    is_stab_move = move_type in actor1.get_types()
    stab_mult = get_ability_stab_multiplier(actor1.get_ability(), is_stab_move)
    type_eff = get_type_effectiveness(move_type, actor2.get_types())

    # Damage-step abilities (e.g. Multiscale, Tinted Lens, Filter)
    damage_mult = get_ability_damage_multiplier(actor1.get_ability(), type_eff, actor1.get_current_hp()) * \
                  get_ability_damage_multiplier(actor2.get_ability(), type_eff, actor2.get_current_hp())

    estimated = calculate_damage(
        move_power=modified_power,
        attack_stat=attack_stat,
        defense_stat=defense_stat,
        stab=stab_mult,
        type_effectiveness=type_eff * damage_mult,
        is_critical=is_critical
    )
    hp = calcuate_hp(actor2)
    
    min_percent = round((estimated[0] / hp) * 100)
    max_percent = round((estimated[-1] / hp) * 100)
    return min_percent, max_percent

def get_set_species_name(mon: Mon) -> str:
    """Returns the species name to look up in SETDEX, falling back to base species for Megas."""
    if mon.name in sets:
        return mon.name
    base_name = get_base_species(mon.name)
    return base_name if base_name in sets else mon.name

def try_find_matching_sets(actor1: Mon, actor2: Mon, move: str, damage_taken: int, is_critical: bool = False):
    """
    Iterates through all available sets for non-extracted Pokemon while keeping 
    extracted Pokemon static.
    """
    spec1 = get_set_species_name(actor1)
    spec2 = get_set_species_name(actor2)

    is_extracted1 = getattr(actor1, "is_extracted", False)
    is_extracted2 = getattr(actor2, "is_extracted", False)

    orig_state1 = (actor1.get_evs().copy(), actor1.get_nature(), actor1.get_item())
    orig_state2 = (actor2.get_evs().copy(), actor2.get_nature(), actor2.get_item())

    # Determine total sets available in SETDEX
    total_sets1 = 1 if is_extracted1 else max(1, get_set_count(spec1))
    total_sets2 = 1 if is_extracted2 else max(1, get_set_count(spec2))

    for set1_idx in range(1, total_sets1 + 1):
        if not is_extracted1:
            evs1 = get_evs(spec1, set1_idx)
            nature1 = get_nature(spec1, set1_idx)
            item1 = get_item(spec1, set1_idx)
            
            if evs1: actor1.set_evs(evs1)
            if nature1: actor1.set_nature(nature1)
            if item1: actor1.set_item(item1)

        for set2_idx in range(1, total_sets2 + 1):
            if not is_extracted2:
                evs2 = get_evs(spec2, set2_idx)
                nature2 = get_nature(spec2, set2_idx)
                item2 = get_item(spec2, set2_idx)
                
                if evs2: actor2.set_evs(evs2)
                if nature2: actor2.set_nature(nature2)
                if item2: actor2.set_item(item2)

            min_p, max_p = simulate_hit(actor1, actor2, move, is_critical=is_critical)
            
            # Check if this combination produces the recorded damage roll
            if min_p <= damage_taken <= max_p:
                matched1 = "Static (Extracted)" if is_extracted1 else f"Set {set1_idx}"
                matched2 = "Static (Extracted)" if is_extracted2 else f"Set {set2_idx}"
                return min_p, max_p, matched1, matched2

    # If no set matches, revert to original stats
    actor1.set_evs(orig_state1[0])
    actor1.set_nature(orig_state1[1])
    actor1.set_item(orig_state1[2])

    actor2.set_evs(orig_state2[0])
    actor2.set_nature(orig_state2[1])
    actor2.set_item(orig_state2[2])

    min_p, max_p = simulate_hit(actor1, actor2, move, is_critical=is_critical)
    return min_p, max_p, None, None

def apply_mega_evolution(mon: Mon, raw_species: str, item: str = ""):
    """Updates the Mon instance with Mega stats, types, ability, and name."""
    mega_species = raw_species
    if item.endswith("ite X") or item.endswith("ite Y"):
        forme_suffix = item.split()[-1]
        mega_species = f"{raw_species}-Mega-{forme_suffix}"
    elif item.endswith("ite") or "Mega" not in mega_species:
        if not mega_species.endswith("-Mega"):
            mega_species = f"{raw_species}-Mega"

    if not get_base_stats(mega_species):
        if get_base_stats(raw_species):
            mega_species = raw_species

    mon.set_name(mega_species)
    mon.set_base_stats(get_base_stats(mega_species))
    mon.set_type(get_types(mega_species))
    
    mega_abilities = get_abilities(mega_species)
    if mega_abilities:
        mon.set_ability(mega_abilities)

def damage(lines):
    actor1 = None
    actor2 = None
    move = None
    is_critical = False
    
    for line in lines:
        if line.startswith("|move|"):
            a1_nick, a2_nick = actors(line)
            actor1 = _mon_for_nickname(a1_nick)
            actor2 = _mon_for_nickname(a2_nick)
            move = line.split("|")[3]
            is_critical = False
        elif line.startswith("|-mega|"):
            parts = line.split("|")
            nickname_val = parts[2]
            raw_species = parts[3].strip()
            item = parts[4].strip() if len(parts) > 4 else ""
            
            mon = _mon_for_nickname(nickname_val)
            if mon:
                apply_mega_evolution(mon, raw_species, item)
        elif line.startswith("|-terastallize|"):
            parts = line.split("|")
            nickname_val = parts[2]
            tera_type = parts[3].strip() if len(parts) > 3 else ""
            
            mon = _mon_for_nickname(nickname_val)
            if mon:
                # need to set the type to the tera type, but also need to store the original types somewhere if we want to revert back
                mon.set_type([tera_type])
        elif line.startswith("|-boost|"):
            parts = line.split("|")
            nickname_val = parts[2]
            stat = parts[3]
            val = int(parts[4])
            _mon_for_nickname(nickname_val).get_boosts()[stat] = val
        elif line.startswith("|-unboost|"):
            parts = line.split("|")
            nickname_val = parts[2]
            stat = parts[3]
            val = int(parts[4])
            _mon_for_nickname(nickname_val).get_boosts()[stat] = -val
        elif line.startswith("|switch|"):
            parts = line.split("|")
            mon = _mon_for_nickname(parts[2])
            if mon:
                mon.set_boosts({
                    "atk": 0, "def": 0, "spa": 0,
                    "spd": 0, "spe": 0, "accuracy": 0, "evasion": 0
                })
        elif line.startswith("|-crit|"):
            is_critical = True
        elif line.startswith("|-damage|"):
            parts = line.split("|")
            nickname_val = parts[2]
            current_hp = 0 if "0 fnt" in parts else int(parts[3].split("/")[0])
            
            mon = _mon_for_nickname(nickname_val)
            actor2 = mon
            
            if mon is not None:
                damage_taken = mon.get_current_hp() - current_hp
                mon.set_current_hp(current_hp)
                
                # Check if this damage came from a residual effect (e.g. [from] item: Life Orb, [from] psn)
                is_residual = any("[from]" in p for p in parts[4:])
                
                # Only calculate combat damage if it was from a direct move hit
                if not is_residual and move is not None and actor1 is not None and damage_taken > 0:
                    crit_tag = " [CRIT]" if is_critical else ""
                    min_percent, max_percent = simulate_hit(actor1, actor2, move, is_critical=is_critical)
                    
                    if min_percent <= damage_taken <= max_percent or actor2.get_current_hp() == 0:
                        print(f"{actor2.name} took valid {damage_taken}% from {move}{crit_tag} from {actor1.name}. Current HP: {current_hp}%. Estimated: {min_percent}% to {max_percent}%")
                    else:
                        min_p, max_p, s1, s2 = try_find_matching_sets(actor1, actor2, move, damage_taken, is_critical=is_critical)
                        if s1 is not None and s2 is not None:
                            print(f"{actor2.name} took valid {damage_taken}% from {move}{crit_tag} from {actor1.name} (Matched using Attacker: {s1}, Defender: {s2}). Estimated: {min_p}% to {max_p}%")
                        else:
                            print(f"{actor2.name} took invalid {damage_taken}% from {move}{crit_tag} from {actor1.name}. Current HP: {current_hp}%. Estimated: {min_percent}% to {max_percent}%. (Mismatch!)")
                    
                    is_critical = False
        elif line.startswith("|-heal|") or line.startswith("|-sethp|"):
            parts = line.split("|")
            nickname_val = parts[2]
            
            # Showdown HP can be formatted as "75/100", "100/100", or "0 fnt"
            if len(parts) > 3 and "/" in parts[3]:
                healed_hp = int(parts[3].split("/")[0])
                mon = _mon_for_nickname(nickname_val)
                if mon:
                    mon.set_current_hp(healed_hp)

def main():
    url = "https://replay.pokemonshowdown.com/gen9natdexdraft-2644608154.json"
    data = fetch_json(url)
    lines = data["log"].splitlines()
    teams(lines)
    nickname(lines)
    _rebuild_nickname_lookup()
    team = "https://pokepast.es/6674218482c4cc60"
    extract(team)
    damage(lines)
    print_paste()

if __name__ == "__main__":
    main()