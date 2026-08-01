from bs4 import BeautifulSoup
import requests
from mon import Mon
import math

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
        if "HP" in ev:
            m.set_hp_ev(ev_value)
        elif "Atk" in ev:
            m.set_atk_ev(ev_value)
        elif "Def" in ev:
            m.set_def_ev(ev_value)
        elif "SpA" in ev:
            m.set_spa_ev(ev_value)
        elif "SpD" in ev:
            m.set_spd_ev(ev_value)
        elif "Spe" in ev:
            m.set_spe_ev(ev_value)
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
    # m.print_paste()

def find_index(mon_data, search_string):
    for i, line in enumerate(mon_data):
        if search_string in line:
            return i
    return -1

def index_exists(mon_data, move_index):
    return move_index < len(mon_data) and move_index >= 0

def calculate_damage(
    attacker_level: int,
    move_power: int,
    attack_stat: int,
    defense_stat: int,
    targets: int = 1,
    weather_multiplier: float = 1.0,
    is_critical: bool = False,
    stab: float = 1.0,
    type_effectiveness: float = 1.0,
    burn_multiplier: float = 1.0,
) -> list[int]:
    """Calculates all 16 possible damage roll outcomes."""
    if move_power == 0:
        return [0]

    # Base damage step
    level_factor = math.floor((2 * attacker_level) / 5) + 2
    base_damage = math.floor(
        (level_factor * move_power * (attack_stat / defense_stat)) / 50
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
    hp = math.floor(((2 * base_hp + 0 + (ev_hp / 4)) * level) / 100) + level + 10
    return hp

def calculate_stat(mon: Mon, stat_name: str) -> int:
    """Calculates a specific stat (other than HP) of a Pokémon based on its base stats, level, and EVs."""
    base_stat = mon.get_base_stats()[stat_name]
    ev_stat = mon.get_evs()[stat_name]
    level = mon.get_level()

    # Stat formula: ((2 * Base + IV + (EV/4)) * Level / 100) + 5
    stat_value = math.floor(((2 * base_stat + 0 + (ev_stat / 4)) * level) / 100) + 5
    return stat_value
   
def main():
    #url = "https://pokepast.es/df340272f67d375e"
    #extract(url)

    # Example Usage:
    rolls = calculate_damage(
    attacker_level=100,
    move_power=90,          # e.g., Thunderbolt
    attack_stat=300,        # Special Attack
    defense_stat=200,       # Special Defense
    stab=1.5,
    type_effectiveness=2.0  # Super effective
    )
    print("Damage Rolls:", rolls)

if __name__ == "__main__":
    main()