from parser import fetch_json, teams
from pathlib import Path

DB_ROOT = Path(__file__).resolve().parent.parent

def public_ability(lines, file):
    for line in lines:
        if line.startswith("|-ability|"):
            parts = line.split("|")
            ability = parts[3].strip("|")

            with open(file, "a") as f:
                f.seek(0)
                if ability not in f.read():
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
    input_file = DB_ROOT / 'DB_CSV' / "replaysDraft.csv"
    output_file = DB_ROOT / 'dex' / "public_abilities.txt"
    get_public_abilities(input_file, output_file)

if __name__ == "__main__":
    main()