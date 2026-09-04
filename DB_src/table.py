import sqlite3
import json
from html import escape
from pathlib import Path

DB_ROOT = Path(__file__).resolve().parent.parent

def _build_table_html(column_names, rows):
    parts = ["<table>"]
    header_cells = "".join(f"<th>{escape(str(name))}</th>" for name in column_names)
    parts.append(f"<tr><th>sprite</th>{header_cells}</tr>")

    for row in rows:
        sprite_path = row[-1] if row[-1] else "sprites/0.png"
        row_cells = "".join(f"<td>{escape(str(value))}</td>" for value in row[:-1])
        sprite_html = (
            f'<td><img src="{escape(sprite_path)}" alt="sprite" '
            'style="height: 40px; width: 40px; object-fit: contain;"/></td>'
        )
        parts.append(f"<tr>{sprite_html}{row_cells}</tr>")

    parts.append("</table>")
    return "\n".join(parts)

def print_table(dbName, tableName, fileName):
    conn = sqlite3.connect(dbName)
    cursor = conn.cursor()

    rows = cursor.execute(
        "SELECT name, points, games_played, winrate, kills, deaths, diff, KPG, "
        "COALESCE(path, 'sprites/0.png') as path FROM mons WHERE games_played > 500.0"
    ).fetchall()
    column_names = ["name", "points", "games_played", "winrate", "kills", "deaths", "diff", "KPG"]

    lookup_rows = cursor.execute(
        "SELECT name, points, games_played, winrate, kills, deaths, diff, KPG, "
        "COALESCE(path, 'sprites/0.png') as path FROM mons ORDER BY name"
    ).fetchall()
    conn.close()

    table_html = _build_table_html(column_names, rows)
    lookup_data = [
        {
            "name": row[0],
            "points": row[1],
            "gamesPlayed": row[2],
            "winrate": row[3],
            "kills": row[4],
            "deaths": row[5],
            "diff": row[6],
            "kpg": row[7],
            "sprite": row[8],
        }
        for row in lookup_rows
    ]
    lookup_data_js = "window.DRAFT_DB_MON_DATA = " + json.dumps(lookup_data, ensure_ascii=True) + ";"

    lookup_data_path = Path(fileName).parent / 'js' / 'mon-data.js'
    lookup_data_path.write_text(lookup_data_js, encoding="utf-8")

    page_html = f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <title>DraftDB Table</title>
    <link rel=\"stylesheet\" href=\"css/style.css\" />
</head>
<body class=\"main-text-color\">
    <div class=\"intro\">
        <a class=\"external-link\" href=\"mon.html\">Mon lookup</a>
{table_html}
    </div>
    <script type=\"text/javascript\" src=\"js/slider.js\"></script>
</body>
</html>
"""
    Path(fileName).write_text(page_html, encoding="utf-8")

def main():
    dbName = DB_ROOT / 'database' / 'monDB.sqlite'
    tableName = 'mons'
    fileName = DB_ROOT / 'index.html'
    print_table(dbName, tableName, fileName)

if __name__ == "__main__":
    main()