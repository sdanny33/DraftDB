from pathlib import Path
import re
from parser import edges, fetch_json

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

def public_ability(lines, file):
    for line in lines:
        if line.startswith("|-ability|"):
            parts = line.split("|")
            ability = parts[3].strip("|")

            with open(file, "a") as f:
                if ability not in file.read_text():
                    f.write(f"{ability}\n")
                    print(f"Added ability: {ability}")

def get_public_abilities(input_file, output_file):
        with open(input_file, 'r') as f:
            for raw in f:
                url = raw.strip()
                data = fetch_json(url)
                lines = data["log"].splitlines()
                public_ability(lines, output_file)


def main():
    # Example usage
    input_file = DB_ROOT / "DB_CSV" /"replaysDraft.csv"
    output_file = DB_ROOT / "dex" / "public_abilities.txt"

    get_public_abilities(input_file, output_file)

if __name__ == "__main__":
    main()