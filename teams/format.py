import csv
from pathlib import Path

DB_ROOT = Path(__file__).resolve().parent.parent

MAX_MOVES = 4
FIELD_PREFIXES = ('Ability:', 'Tera Type:', 'EVs:', 'Level:', 'Shiny:', 'Happiness:', 'IVs:')

def is_move(line):
    return line.startswith('- ')

def is_header(line):
    """A header is the 'Name @ Item' line that starts each mon."""
    return not (
        is_move(line)
        or line.startswith(FIELD_PREFIXES)
        or line.endswith(' Nature')
    )

def split_mons(lines):
    """Group lines into one list per mon. A new mon starts at each header line,
    so mons can have 1-4 moves (or be missing a field) without breaking alignment."""
    mons = []
    current = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if is_header(line) and current:
            mons.append(current)
            current = []
        current.append(line)
    if current:
        mons.append(current)
    return mons

def parse_mon(chunk):
    header = chunk[0]
    if '@' in header:
        name, item = header.split('@', 1)
    else:
        name, item = header, ''

    ability = tera = evs = nature = ''
    moves = []
    for line in chunk[1:]:
        if line.startswith('Ability:'):
            ability = line.removeprefix('Ability:').strip()
        elif line.startswith('Tera Type:'):
            tera = line.removeprefix('Tera Type:').strip()
        elif line.startswith('EVs:'):
            evs = line.removeprefix('EVs:').strip()
        elif line.endswith(' Nature'):
            nature = line.removesuffix(' Nature').strip()
        elif is_move(line):
            moves.append(line.removeprefix('- ').strip())

    moves = (moves + [''] * MAX_MOVES)[:MAX_MOVES]  # pad to 4 columns
    return [name.strip(), item.strip(), ability, tera, evs, nature, *moves]

def format(path, output_path):
    with open(path, 'r') as f:
        lines = [line.rstrip('\n') for line in f]

    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f)
        for chunk in split_mons(lines):
            writer.writerow(parse_mon(chunk))

def main():
    format(DB_ROOT / 'teams' / 'output.csv', DB_ROOT / 'teams' / 'teams.csv')

if __name__ == "__main__":
    main()