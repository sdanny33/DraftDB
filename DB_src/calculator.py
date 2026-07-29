
from os import link
from urllib import response
from bs4 import BeautifulSoup
import requests
from mon import Mon

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
    
     
def main():
    url = "https://pokepast.es/df340272f67d375e"
    extract(url)

if __name__ == "__main__":
    main()