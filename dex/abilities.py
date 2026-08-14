from DB_src import mon
from DB_src import populateInfo

def check_ability(m):
    if m.get_ability is "Huge Power" or m.get_ability is "Pure Power":
        m.boosts["atk"] = 2
    if m.get_ability is "Hustle":
        m.boosts["atk"] = 1
    if m.get_ability is "Guts":
        if m.get_item is "Flame Orb" or m.get_item is "Toxic Orb":
            m.boosts["atk"] = 1
    if m.get_ability is "Overgrow":
        if populateInfo.get_move_type() is "Grass" and m.get_current_hp() <= 33:
            m.boosts["atk"] = 1
            m.boosts["spa"] = 1
        else:
            m.boosts["atk"] = 0
            m.boosts["spa"] = 0
    if m.get_ability is "Blaze":
        if populateInfo.get_move_type() is "Fire" and m.get_current_hp() <= 33:
            m.boosts["atk"] = 1
            m.boosts["spa"] = 1
        else:
            m.boosts["atk"] = 0
            m.boosts["spa"] = 0
    if m.get_ability is "Torrent":
        if populateInfo.get_move_type() is "Water" and m.get_current_hp() <= 33:
            m.boosts["atk"] = 1
            m.boosts["spa"] = 1
        else:
            m.boosts["atk"] = 0
            m.boosts["spa"] = 0
    if m.get_ability is "Swarm":
        if populateInfo.get_move_type() is "Bug" and m.get_current_hp() <= 33:
            m.boosts["atk"] = 1
            m.boosts["spa"] = 1
        else:
            m.boosts["atk"] = 0
            m.boosts["spa"] = 0
    if m.get_ability is "Rivalry":
        # Rivalry boosts attack against Pokémon of the same gender and lowers it against Pokémon of the opposite gender.
        pass  # This ability's effect is context-dependent and requires additional information about the opponent's gender.
    if m.get_ability is "Iron Fist":
        m.boosts["atk"] = 1
    if m.get_ability is "Adaptability":
        stab_multiplier = 2.0  # This ability increases the STAB multiplier from 1.5 to 2.0.
    if m.get_ability is "Solar Power":
        # Solar Power boosts Special Attack in sunny weather but also causes the Pokémon to lose some HP each turn. The boost is context-dependent and requires additional information about the weather.
        pass
    if m.get_ability is "Normalize":
        # Normalize changes all moves to Normal type and boosts their power. The boost is context-dependent and requires additional information about the moves being used.
        pass
    if m.get_ability is "Technician":
        # Technician boosts the power of moves with a base power of 60 or less by 50%. The boost is context-dependent and requires additional information about the moves being used.
        pass
    if m.get_ability is "Tinted Lens":
        # Tinted Lens doubles the damage of "not very effective" moves. The boost is context-dependent and requires additional information about the moves being used.
        pass
    if m.get_ability is "Filter":
        # Filter reduces the damage taken from "super effective" moves. The boost is context-dependent and requires additional information about the moves being used.
        pass
    if m.get_ability is "Reckless":
        # Reckless boosts the power of moves that have recoil damage. The boost is context-dependent and requires additional information about the moves being used.
        pass
    if m.get_ability is "Sheer Force":
        # Sheer Force boosts the power of moves that have secondary effects but removes those effects. The boost is context-dependent and requires additional information about the moves being used.
        pass
    if m.get_ability is "Defeatist":
        if m.get_current_hp() <= 50:
            m.boosts["atk"] = -1
            m.boosts["spa"] = -1
        else:
            m.boosts["atk"] = 0
            m.boosts["spa"] = 0
    if m.get_ability is "Toxic Boost":
        if m.get_item is "Toxic Orb":
            m.boosts["atk"] = 1
    if m.get_ability is "Flare Boost":
        if m.get_item is "Flame Orb":
            m.boosts["spa"] = 1
    if m.get_ability is "Analytic":
        m.boosts["spa"] = 1
    if m.get_ability is "Infiltraitor":
        # This ability allows the Pokémon to bypass certain defensive moves and abilities, but it doesn't directly boost stats.
        pass
    if m.get_ability is "Sand Force":
        # This ability boosts the power of Rock, Ground, and Steel-type moves by 30% in a sandstorm, but it doesn't directly boost stats.
        pass
    if m.get_ability is "Protean":
        # This ability changes the Pokémon's type to the type of the move it's about to use, but it doesn't directly boost stats.
        pass
    if m.get_ability is "Mega Launcher":
        # This ability boosts the power of aura and pulse moves by 50%, but it doesn't directly boost stats.
        pass
    if m.get_ability is "Tough Claws":
        # This ability boosts the power of moves that make direct contact by 30%, but it doesn't directly boost stats.
        pass
    if m.get_ability is "Pixilate":
        # This ability turns Normal-type moves into Fairy-type moves and boosts their power by 20%, but it doesn't directly boost stats.
        pass
    if m.get_ability is "Aerilate":
        # This ability turns Normal-type moves into Flying-type moves and boosts their power by 20%, but it doesn't directly boost stats.
        pass
    if m.get_ability is "Parental Bond":
        m.boosts["atk"] = 1
    if m.get_ability is "Dark Aura":
        if populateInfo.get_move_type() is "Dark":
            populateInfo.get_move_base_power() * 1.33
    if m.get_ability is "Fairy Aura":
        if populateInfo.get_move_type() is "Fairy":
            populateInfo.get_move_base_power() * 1.33
    if m.get_ability is "Water Bubble":
        if populateInfo.get_move_type() is "Water":
            populateInfo.get_move_base_power() * 1.5
    if m.get_ability is "Steel Worker":
        if populateInfo.get_move_type() is "Steel":
            populateInfo.get_move_base_power() * 1.5
    if m.get_ability is "Galvanize":
        # This ability turns Normal-type moves into Electric-type moves and boosts their power by 20%, but it doesn't directly boost stats.
        pass
    if m.get_ability is "Fluffy":
        # This ability halves the damage taken from moves that make direct contact but doubles the damage taken from Fire-type moves. It doesn't directly boost stats.
        pass
    if m.get_ability is "Shadow Shield" or m.get_ability is "Multiscale":
        if m.get_current_hp() == 100:  # Assuming max HP is 100 for simplicity; adjust as needed
            m.boosts["def"] = 1
            m.boosts["spd"] = 1
        else:
            m.boosts["def"] = 0
            m.boosts["spd"] = 0
    if m.get_ability is "Prism Armor":
       # This ability reduces the damage taken from super effective moves by 25%, but it doesn't directly boost stats.
       pass
    if m.get_ability is "Neuroforce":
        # This ability boosts the power of super effective moves by 25%, but it doesn't directly boost stats.
        pass
    if m.get_ability is "Punk Rock":
        # This ability boosts the power of sound-based moves by 30% and reduces damage taken from sound-based moves by 50%, but it doesn't directly boost stats.
        pass
    if m.get_ability is "Steely Spirit":
        if populateInfo.get_move_type() is "Steel":
            populateInfo.get_move_base_power() * 1.5
    if m.get_ability is "Gorilla Tactics":
        m.boosts["atk"] = 1
    if m.get_ability is "Transistor":
        if populateInfo.get_move_type() is "Electric":
            populateInfo.get_move_base_power() * 1.3
    if m.get_ability is "Dragons Maw":
        if populateInfo.get_move_type() is "Dragon":
            populateInfo.get_move_base_power() * 1.3
    if m.get_ability is "Rocky Payload":
        if populateInfo.get_move_type() is "Rock":
            populateInfo.get_move_base_power() * 1.3
    if m.get_ability is "Vessel of Ruin":
        # This ability reduces the power of moves used by other Pokémon by 20%, but it doesn't directly boost stats.
        pass
    if m.get_ability is "Sword of Ruin":
        # This ability reduces the Defense of all other Pokémon by 1 stage, but it doesn't directly boost stats.
        pass
    if m.get_ability is "Tablets of Ruin":
        # This ability reduces the Special Defense of all other Pokémon by 1 stage, but it doesn't directly boost stats.
        pass
    if m.get_ability is "Beads of Ruin":
        # This ability reduces the Special Attack of all other Pokémon by 1 stage, but it doesn't directly boost stats.
        pass
    if m.get_ability is "Orichalcum Pulse":
        # This ability boosts the power of Steel-type moves by 30% and reduces damage taken from Steel-type moves by 50%, but it doesn't directly boost stats.
        pass
    if m.get_ability is "Hadron Engine":
        # This ability boosts the power of Electric-type moves by 30% and reduces damage taken from Electric-type moves by 50%, but it doesn't directly boost stats.
        pass
    if m.get_ability is "Sharpness":
        # This ability boosts the power of slicing moves by 30%, but it doesn't directly boost stats.
        pass
    if m.get_ability is "Dragonize":
       # This ability boosts the power of Dragon-type moves by 30%, but it doesn't directly boost stats.
       pass
    if m.get_ability is "Fire Mane":
        if populateInfo.get_move_type() is "Fire":
            populateInfo.get_move_base_power() * 1.5