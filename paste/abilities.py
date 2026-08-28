def check_ability(m):
    if m.get_ability == "Rivalry":
        # Rivalry boosts attack against Pokémon of the same gender and lowers it against Pokémon of the opposite gender.
        pass  # This ability's effect is context-dependent and requires additional information about the opponent's gender.
    if m.get_ability == "Iron Fist":
        # Iron Fist boosts the power of punching moves by 20%. The boost is context-dependent and requires additional information about the moves being used.
        pass
    if m.get_ability == "Solar Power":
        # Solar Power boosts Special Attack in sunny weather but also causes the Pokémon to lose some HP each turn. The boost is context-dependent and requires additional information about the weather.
        pass
    if m.get_ability == "Reckless":
        # Reckless boosts the power of moves that have recoil damage. The boost is context-dependent and requires additional information about the moves being used.
        pass
    if m.get_ability == "Sheer Force":
        # Sheer Force boosts the power of moves that have secondary effects but removes those effects. The boost is context-dependent and requires additional information about the moves being used.
        pass
    if m.get_ability == "Analytic":
        # Analytic boosts the power of moves if the Pokémon moves last. The boost is context-dependent and requires additional information about the turn order.
        pass
    if m.get_ability == "Infiltraitor":
        # This ability allows the Pokémon to bypass certain defensive moves and abilities, but it doesn't directly boost stats.
        pass
    if m.get_ability == "Sand Force":
        # This ability boosts the power of Rock, Ground, and Steel-type moves by 30% in a sandstorm, but it doesn't directly boost stats.
        pass
    if m.get_ability == "Protean":
        # This ability changes the Pokémon's type to the type of the move it's about to use, but it doesn't directly boost stats.
        pass
    if m.get_ability == "Mega Launcher":
        # This ability boosts the power of aura and pulse moves by 50%, but it doesn't directly boost stats.
        pass
    if m.get_ability == "Tough Claws":
        # This ability boosts the power of moves that make direct contact by 30%, but it doesn't directly boost stats.
        pass
    if m.get_ability == "Parental Bond":
        # This ability allows the Pokémon to hit twice with damaging moves, but it doesn't directly boost stats.
        pass
    if m.get_ability == "Fluffy":
        # This ability halves the damage taken from moves that make direct contact but doubles the damage taken from Fire-type moves. It doesn't directly boost stats.
        pass
    if m.get_ability == "Punk Rock":
        # This ability boosts the power of sound-based moves by 30% and reduces damage taken from sound-based moves by 50%, but it doesn't directly boost stats.
        pass
    if m.get_ability == "Vessel of Ruin":
        # This ability reduces the power of moves used by other Pokémon by 20%, but it doesn't directly boost stats.
        pass
    if m.get_ability == "Sword of Ruin":
        # This ability reduces the Defense of all other Pokémon by 1 stage, but it doesn't directly boost stats.
        pass
    if m.get_ability == "Tablets of Ruin":
        # This ability reduces the Special Defense of all other Pokémon by 1 stage, but it doesn't directly boost stats.
        pass
    if m.get_ability == "Beads of Ruin":
        # This ability reduces the Special Attack of all other Pokémon by 1 stage, but it doesn't directly boost stats.
        pass
    if m.get_ability == "Orichalcum Pulse":
        # This ability boosts the power of Steel-type moves by 30% and reduces damage taken from Steel-type moves by 50%, but it doesn't directly boost stats.
        pass
    if m.get_ability == "Hadron Engine":
        # This ability boosts the power of Electric-type moves by 30% and reduces damage taken from Electric-type moves by 50%, but it doesn't directly boost stats.
        pass
    if m.get_ability == "Sharpness":
        # This ability boosts the power of slicing moves by 30%, but it doesn't directly boost stats.
        pass

# abilities.py

PINCH_ABILITIES = {
    "Overgrow": "Grass",
    "Blaze": "Fire",
    "Torrent": "Water",
    "Swarm": "Bug"
}

TYPE_BOOST_ABILITIES = {
    "Steelworker": ("Steel", 1.5),
    "Steely Spirit": ("Steel", 1.5),
    "Transistor": ("Electric", 1.3),
    "Dragon's Maw": ("Dragon", 1.5),
    "Dragons Maw": ("Dragon", 1.5),
    "Rocky Payload": ("Rock", 1.5),
    "Water Bubble": ("Water", 2.0),
    "Dark Aura": ("Dark", 1.33),
    "Fairy Aura": ("Fairy", 1.33),
    "Fire Mane": ("Fire", 1.5),
}

ATE_ABILITIES = {
    "Pixilate": "Fairy",
    "Aerilate": "Flying",
    "Galvanize": "Electric",
    "Dragonize": "Dragon"
}

def _normalize_abilities(ability) -> list[str]:
    """Helper to convert ability strings, slash-separated strings, or lists into a list of strings."""
    if isinstance(ability, list):
        # Flatten and split any slash-separated entries inside the list
        res = []
        for a in ability:
            res.extend([sub.strip() for sub in str(a).split("/") if sub.strip()])
        return res
    if isinstance(ability, str):
        return [sub.strip() for sub in ability.split("/") if sub.strip()]
    return []

def get_ability_stat_multiplier(ability, stat_name: str, item: str = "", current_hp_percent: int = 100) -> float:
    abilities = _normalize_abilities(ability)
    
    if any(ab in ("Huge Power", "Pure Power") for ab in abilities) and stat_name == "atk":
        return 2.0
    if any(ab in ("Gorilla Tactics", "Hustle") for ab in abilities) and stat_name == "atk":
        return 1.5

    if "Guts" in abilities and stat_name == "atk" and item in ("Flame Orb", "Toxic Orb"):
        return 1.5
    if "Toxic Boost" in abilities and stat_name == "atk" and item == "Toxic Orb":
        return 1.5
    if "Flare Boost" in abilities and stat_name == "spa" and item == "Flame Orb":
        return 1.5

    if "Defeatist" in abilities and current_hp_percent <= 50 and stat_name in ("atk", "spa"):
        return 0.5

    return 1.0


def get_ability_power_multiplier(ability, move_type: str, raw_base_power: int = 0, current_hp_percent: int = 100) -> float:
    abilities = _normalize_abilities(ability)

    for ab in abilities:
        if ab in PINCH_ABILITIES and PINCH_ABILITIES[ab] == move_type and current_hp_percent <= 33:
            return 1.5
        if ab in TYPE_BOOST_ABILITIES:
            boosted_type, mult = TYPE_BOOST_ABILITIES[ab]
            if move_type == boosted_type:
                return mult
        if ab == "Technician" and 0 < raw_base_power <= 60:
            return 1.5
        if ab in ATE_ABILITIES and move_type == "Normal":
            return 1.2

    return 1.0


def get_ability_damage_multiplier(ability, type_effectiveness: float, current_hp_percent: int = 100) -> float:
    abilities = _normalize_abilities(ability)

    if any(ab in ("Multiscale", "Shadow Shield") for ab in abilities) and current_hp_percent >= 100:
        return 0.5
    if any(ab in ("Filter", "Solid Rock", "Prism Armor") for ab in abilities) and type_effectiveness > 1.0:
        return 0.75

    if "Tinted Lens" in abilities and type_effectiveness < 1.0:
        return 2.0
    if "Neuroforce" in abilities and type_effectiveness > 1.0:
        return 1.25

    return 1.0


def get_ability_stab_multiplier(ability, is_stab_move: bool) -> float:
    abilities = _normalize_abilities(ability)
    if "Adaptability" in abilities and is_stab_move:
        return 2.0
    return 1.5 if is_stab_move else 1.0

def get_effective_move_type(ability, move_type: str) -> str:
    """Handles type overrides for Normalize and -ate abilities."""
    abilities = _normalize_abilities(ability)

    if "Normalize" in abilities:
        return "Normal"

    for ab in abilities:
        if ab in ATE_ABILITIES and move_type == "Normal":
            return ATE_ABILITIES[ab]

    return move_type