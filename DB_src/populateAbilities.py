from pathlib import Path
import re

DB_ROOT = Path(__file__).resolve().parent.parent


def _normalize_name(name):
    return re.sub(r"[^a-z0-9]", "", name.lower())


def get_abilities(name):
    file = DB_ROOT / "dex" / "pokedex.ts"
    text = file.read_text()
    normalized_name = _normalize_name(name)

    pattern = re.compile(
        r'name:\s*"(?P<name>[^"]+)".*?abilities:\s*\{(?P<abilities>.*?)\}',
        re.DOTALL,
    )

    for match in pattern.finditer(text):
        if _normalize_name(match.group("name")) != normalized_name:
            continue

        abilities = re.findall(r':\s*"([^"]+)"', match.group("abilities"))
        return abilities

    return []

def populate_abilities(team1, team2):
    for i in range(min(6, len(team1), len(team2))):
        if team1[i].name:
            abilities = get_abilities(team1[i].name)
            if abilities:
                team1[i].set_ability(" / ".join(abilities))
        if team2[i].name:
            abilities = get_abilities(team2[i].name)
            if abilities:
                team2[i].set_ability(" / ".join(abilities))

def main():
    # Example usage
    from mon import Mon

    team1 = [Mon("Bulbasaur"), Mon("Charmander"), Mon("Squirtle")]
    team2 = [Mon("Pikachu"), Mon("Eevee"), Mon("Jigglypuff")]

    populate_abilities(team1, team2)

    for mon in team1 + team2:
        print(f"{mon.name} has ability: {mon.ability}")

if __name__ == "__main__":
    main()