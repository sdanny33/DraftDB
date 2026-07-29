
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
    m.set_name(mon_data[0].split(" @ ")[0])
    m.set_item(mon_data[0].split(" @ ")[1])
    m.set_ability(mon_data[1].split("Ability: ")[1])

    # m.set_evs(mon_data[find_index(mon_data, "EVs: ")].split("EVs: "))
    m.set_nature(mon_data[find_index(mon_data, " Nature")].split(" Nature")[0])
    move_index = find_index(mon_data, "- ")
    m.add_moves(mon_data[move_index].split("- "))
    if index_exists(mon_data, move_index + 1):
        m.add_moves(mon_data[move_index + 1].split("- "))
    if index_exists(mon_data, move_index + 2):
        m.add_moves(mon_data[move_index + 2].split("- "))
    if index_exists(mon_data, move_index + 3):
        m.add_moves(mon_data[move_index + 3].split("- "))
    m.print_paste()

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