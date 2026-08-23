from mon import Mon
from populateInfo import get_move_base_power, get_move_type

# --- Item Calculation Helpers ---

TYPE_BOOST_ITEMS = {
    "Black Belt": "Fighting",
    "Black Glasses": "Dark",
    "Charcoal": "Fire",
    "Dragon Fang": "Dragon",
    "Fairy Feather": "Fairy",
    "Hard Stone": "Rock",
    "Magnet": "Electric",
    "Metal Coat": "Steel",
    "Miracle Seed": "Grass",
    "Mystic Water": "Water",
    "Never-Melt Ice": "Ice",
    "Poison Barb": "Poison",
    "Sharp Beak": "Flying",
    "Silk Scarf": "Normal",
    "Silver Powder": "Bug",
    "Soft Sand": "Ground",
    "Spell Tag": "Ghost",
    "Twisted Spoon": "Psychic",
}

def get_item_power_multiplier(item: str, move_type: str) -> float:
    """Calculates base power modifiers based on held items."""
    if item == "Life Orb":
        return 1.3
    if item in TYPE_BOOST_ITEMS and TYPE_BOOST_ITEMS[item] == move_type:
        return 1.2
    return 1.0

def get_item_stat_multiplier(item: str, stat_name: str) -> float:
    """Calculates flat stat multipliers based on held items."""
    if stat_name == "atk" and item == "Choice Band":
        return 1.5
    if stat_name == "spa" and item == "Choice Specs":
        return 1.5
    if stat_name == "spd" and item == "Assault Vest":
        return 1.5
    if stat_name in ("def", "spd") and item == "Eviolite":
        return 1.5
    return 1.0