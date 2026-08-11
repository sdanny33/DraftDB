from DB_src import mon
from DB_src import populateInfo

m = mon.Mon()

if m.get_item() is "Assault Vest":
    m.boosts["spa"] = 1
if m.get_item() is "Choice Specs":
    m.boosts["spa"] = 1
if m.get_item() is "Choice Band":
    m.boosts["atk"] = 1
if m.get_item() is "Choice Scarf":
    m.boosts["spe"] = 1
if m.get_item() is "Life Orb":
    populateInfo.get_move_base_power() * 1.3
if m.get_item() is "Eviolite":
    m.boosts["def"] = 1
    m.boosts["spd"] = 1
if m.get_item() is "Black Belt":
    if populateInfo.get_move_type() is "Fighting":
        populateInfo.get_move_base_power() * 1.2
if m.get_item() is "Black Glasses":
    if populateInfo.get_move_type() is "Dark":
        populateInfo.get_move_base_power() * 1.2
if m.get_item() is "Charcoal":
    if populateInfo.get_move_type() is "Fire":
        populateInfo.get_move_base_power() * 1.2
if m.get_item() is "Dragon Fang":
    if populateInfo.get_move_type() is "Dragon":
        populateInfo.get_move_base_power() * 1.2
if m.get_item() is "Fairy Feather":
    if populateInfo.get_move_type() is "Fairy":
        populateInfo.get_move_base_power() * 1.2
if m.get_item() is "Hard Stone":
    if populateInfo.get_move_type() is "Rock":
        populateInfo.get_move_base_power() * 1.2
if m.get_item() is "Magnet":
    if populateInfo.get_move_type() is "Electric":
        populateInfo.get_move_base_power() * 1.2
if m.get_item() is "Metal Coat":
    if populateInfo.get_move_type() is "Steel":
        populateInfo.get_move_base_power() * 1.2
if m.get_item() is "Miracle Seed":
    if populateInfo.get_move_type() is "Grass":
        populateInfo.get_move_base_power() * 1.2
if m.get_item() is "Mystic Water":
    if populateInfo.get_move_type() is "Water":
        populateInfo.get_move_base_power() * 1.2
if m.get_item() is "Never-Melt Ice":
    if populateInfo.get_move_type() is "Ice":
        populateInfo.get_move_base_power() * 1.2
if m.get_item() is "Poison Barb":
    if populateInfo.get_move_type() is "Poison":
        populateInfo.get_move_base_power() * 1.2
if m.get_item() is "Sharp Beak":
    if populateInfo.get_move_type() is "Flying":
        populateInfo.get_move_base_power() * 1.2
if m.get_item() is "Silk Scarf":
    if populateInfo.get_move_type() is "Normal":
        populateInfo.get_move_base_power() * 1.2
if m.get_item() is "Silver Powder":
    if populateInfo.get_move_type() is "Bug":
        populateInfo.get_move_base_power() * 1.2
if m.get_item() is "Soft Sand":
    if populateInfo.get_move_type() is "Ground":
        populateInfo.get_move_base_power() * 1.2
if m.get_item() is "Spell Tag":
    if populateInfo.get_move_type() is "Ghost":
        populateInfo.get_move_base_power() * 1.2
if m.get_item() is "Twisted Spoon":
    if populateInfo.get_move_type() is "Psychic":
        populateInfo.get_move_base_power() * 1.2