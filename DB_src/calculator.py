from bs4 import BeautifulSoup
import requests
from mon import Mon
import math
from parser import _mon_for_nickname, _rebuild_nickname_lookup, fetch_json, actors, teams, nickname, players
import populateInfo

def extract(url):
        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find all <pre> tags and extract text
            all_pre = soup.find_all('pre')
            for pre in all_pre:
                extract = pre.get_text()
                set_mon_data(extract)

def set_mon_data(info):
    m = Mon("")
    mon_data = info.splitlines()
    #name
    m.set_name(mon_data[0].split(" @ ")[0])
    #item
    m.set_item(mon_data[0].split(" @ ")[1])
    #ability
    m.set_ability(mon_data[1].strip("Ability: "))
    #nature
    m.set_nature(mon_data[find_index(mon_data, " Nature")].split(" Nature")[0])
    # evs
    evs_line = mon_data[find_index(mon_data, "EVs: ")]
    evs_values = evs_line.removeprefix("EVs: ").split("/")
    evs_values = [ev.strip() for ev in evs_values]  # Remove leading/trailing whitespace
    for ev in evs_values:
        ev_value = int(ev.split(" ")[0])
        ev_stat = ev.split(" ")[1]
        m.evs[ev_stat.lower()] = ev_value
    #moves
    move_index = find_index(mon_data, "- ")
    m.add_moves([mon_data[move_index].strip().removeprefix("- ").strip()])
    if index_exists(mon_data, move_index + 1):
        m.add_moves([mon_data[move_index + 1].strip().removeprefix("- ").strip()])
    if index_exists(mon_data, move_index + 2):
        m.add_moves([mon_data[move_index + 2].strip().removeprefix("- ").strip()])
    if index_exists(mon_data, move_index + 3):
        m.add_moves([mon_data[move_index + 3].strip().removeprefix("- ").strip()])
    # print
    m.print_paste()

def find_index(mon_data, search_string):
    for i, line in enumerate(mon_data):
        if search_string in line:
            return i
    return -1

def index_exists(mon_data, move_index):
    return move_index < len(mon_data) and move_index >= 0

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
    print(f"Calculating damage with parameters: move_power={move_power}, attack_stat={attack_stat}, defense_stat={defense_stat}, attacker_level={attacker_level}, targets={targets}, weather_multiplier={weather_multiplier}, is_critical={is_critical}, stab={stab}, type_effectiveness={type_effectiveness}, burn_multiplier={burn_multiplier}")
    if move_power == 0:
        return [0]

    # Base damage step
    level_factor = math.floor((2 * attacker_level) / 5) + 2
    base_damage = math.floor(
        math.floor((level_factor * move_power * (attack_stat / defense_stat))) / 50
    ) + 2

    # Modifier stacking
    modifier = 1.0
    if targets > 1:
        modifier *= 0.75
    if weather_multiplier != 1.0:
        modifier *= weather_multiplier
    if is_critical:
        modifier *= 1.5
    
    # Apply STAB, Type, and Status
    modifier *= stab * type_effectiveness * burn_multiplier

    # Compute all 16 damage rolls (85% to 100%)
    damage_rolls = []
    for roll in range(85, 101):
        final_damage = math.floor(base_damage * (roll / 100.0) * modifier)
        damage_rolls.append(max(1, final_damage))

    return damage_rolls  

def calcuate_hp(mon: Mon) -> int:
    """Calculates the HP of a Pokémon based on its base stats, level, and EVs."""
    base_hp = mon.get_base_stats()["hp"]
    ev_hp = mon.get_evs()["hp"]
    level = mon.get_level()

    # HP formula: ((2 * Base + IV + (EV/4)) * Level / 100) + Level + 10
    hp = math.floor(((2 * base_hp + 31 + math.floor(ev_hp / 4)) * level) / 100) + level + 10
    return hp

def calculate_stat(mon: Mon, stat_name: str) -> int:
    """Calculates a specific stat (other than HP) of a Pokémon based on its base stats, level, and EVs."""
    base_stat = mon.get_base_stats()[stat_name]
    ev_stat = mon.get_evs()[stat_name]
    level = mon.get_level()
    boosts = mon.get_boosts()

    # Stat formula: ((2 * Base + IV + (EV/4)) * Level / 100) + 5
    stat_value = math.floor((math.floor(((2 * base_stat + 31 + math.floor(ev_stat / 4)) * level) / 100) + 5) * calculate_nature_modifiers(mon, stat_name))
    # if stat_name in boosts:
    #     boost_stage = boosts[stat_name]
    #     if boost_stage > 0:
    #         stat_value = math.floor(stat_value * (1 + 0.5 * boost_stage))
    #     elif boost_stage < 0:
    #         stat_value = math.floor(stat_value * (1 + 0.5 * boost_stage))  # Negative boosts reduce the stat
    return stat_value

def calcuate_hp_evs(mon: Mon, evs: int) -> int:
    """Calculates the HP of a Pokémon based on its base stats, level, and EVs."""
    base_hp = mon.get_base_stats()["hp"]
    ev_hp = evs
    level = mon.get_level()

    # HP formula: ((2 * Base + IV + (EV/4)) * Level / 100) + Level + 10
    hp = math.floor(((2 * base_hp + 31 + math.floor(ev_hp / 4)) * level) / 100) + level + 10
    return hp

def calculate_stat_evs(mon: Mon, stat_name: str, evs: int) -> int:
    """Calculates a specific stat (other than HP) of a Pokémon based on its base stats, level, and EVs."""
    base_stat = mon.get_base_stats()[stat_name]
    ev_stat = evs
    level = mon.get_level()
    boosts = mon.get_boosts()

    # Stat formula: ((2 * Base + IV + (EV/4)) * Level / 100) + 5
    stat_value = math.floor((math.floor(((2 * base_stat + 31 + math.floor(ev_stat / 4)) * level) / 100) + 5) * calculate_nature_modifiers(mon, stat_name))
    # if stat_name in boosts:
    #     boost_stage = boosts[stat_name]
    #     if boost_stage > 0:
    #         stat_value = math.floor(stat_value * (1 + 0.5 * boost_stage))
    #     elif boost_stage < 0:
    #         stat_value = math.floor(stat_value * (1 + 0.5 * boost_stage))  # Negative boosts reduce the stat
    return stat_value

def calculate_nature_modifiers(mon: Mon, stat_name: str) -> float:
    """Calculates the nature modifiers for a specific stat of a Pokémon."""
    nature = mon.get_nature()
    if not nature:
        return 1.0

    modifiers = populateInfo.get_nature_modifiers(nature)
    return modifiers.get(stat_name, 1.0)

def is_stab(move_type: str, mon_types: list[str]) -> int:
    """Checks if a move gets STAB (Same Type Attack Bonus) based on the Pokémon's types."""
    if move_type in mon_types:
        return 1.5  # STAB multiplier
    return 1.0  # No STAB

def get_type_effectiveness(move_type: str, target_types: list[str]) -> float:
    """Calculates the type effectiveness multiplier based on the move's type and the target Pokémon's types."""
    type_chart = populateInfo.get_type_chart()
    print(f"Calculating type effectiveness for move type '{move_type}' against target types {target_types}")
    effectiveness = 1.0

    for target_type in target_types:
        if move_type in type_chart and target_type in type_chart[move_type]:
            effectiveness *= type_chart[move_type][target_type]

    return effectiveness

def turn(lines):
    actor1 = None
    actor2 = None
    for line in lines:
        if line.startswith("|move|"):
            actor1, actor2 = actors(line)
            move = line.split("|")[3]
        if line.startswith("|-damage|"):
            parts = line.split("|")
            nickname = parts[2]
            if "0 fnt" in parts:
                current_hp = 0
            else:
                current_hp = int(parts[3].split("/")[0])
            mon = _mon_for_nickname(nickname)
            if mon is not None:
                damage = mon.get_current_hp() - current_hp
                mon.set_current_hp(current_hp)
                print(f"{mon.name} took damage {damage}, current HP: {mon.current_hp}, alive: {mon.alive}")
            else:
                print(f"Could not find Pokémon with nickname: {nickname}")

def boosts(lines):
    # boosts should not stay if the Pokemon is switched out, so we need to reset them if the Pokemon is switched out
    for line in lines:
        if line.startswith("|-boost|"):
            parts = line.split("|")
            nickname = parts[2]
            boosts_str = parts[3]
            boosts_dict = {}
            for boost in boosts_str.split(","):
                stat, value = boost.split("=")
                boosts_dict[stat] = int(value)
            mon = _mon_for_nickname(nickname)
            if mon is not None:
                mon.set_boosts(boosts_dict)
                print(f"{mon.name} had its boosts updated to: {boosts_dict}")
        if line.startswith("|-unboost|"):
            parts = line.split("|")
            nickname = parts[2]
            unboosts_str = parts[3]
            unboosts_dict = {}
            for unboost in unboosts_str.split(","):
                stat, value = unboost.split("=")
                unboosts_dict[stat] = int(value)
            mon = _mon_for_nickname(nickname)
            if mon is not None:
                current_boosts = mon.get_boosts()
                for stat, value in unboosts_dict.items():
                    if stat in current_boosts:
                        current_boosts[stat] += value
                    else:
                        current_boosts[stat] = value
                mon.set_boosts(current_boosts)
                print(f"{mon.name} had its boosts updated to: {current_boosts}")

def test():
        m = Mon("Pikachu")
        m.set_evs(populateInfo.get_evs("Pikachu"))
    
        m2 = Mon("Blastoise")
        m2.set_evs(populateInfo.get_evs("Blastoise"))
    
        # Example Usage:
        rolls = calculate_damage(
            move_power=populateInfo.get_move_base_power("Thunderbolt"),          # e.g., Thunderbolt
            attack_stat=calculate_stat(m, "spa"),        # Special Attack
            defense_stat=calculate_stat(m2, "spd"),       # Special Defense
            stab=is_stab(populateInfo.get_move_type("Thunderbolt"), m.get_types()),
            type_effectiveness=get_type_effectiveness(populateInfo.get_move_type("Thunderbolt"), m2.get_types()),
        )
        print("Damage Rolls:", rolls)
        calculated_hp = calcuate_hp(m2)
        min_percent = ((calculated_hp - rolls[-1]) / calculated_hp) * 100
        max_percent = ((calculated_hp - rolls[0]) / calculated_hp) * 100
        print(f"{m2.name}: {min_percent:.2f} to {max_percent:.2f} percent")
    
def main():
    #team = "https://pokepast.es/4840cb0f46311589"
    #extract(team)

    url = "https://replay.pokemonshowdown.com/gen9natdexdraft-2636733351.json"
    data = fetch_json(url)
    lines = data["log"].splitlines()
    teams(lines)
    nickname(lines)
    _rebuild_nickname_lookup()
    turn(lines)


if __name__ == "__main__":
    main()