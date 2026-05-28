import sqlite3
from html import escape
from pathlib import Path

DB_ROOT = Path(__file__).resolve().parent.parent


def _build_table_html(column_names, rows):
    parts = ["<table>", "<tr>"]
    parts.append("<th>sprite</th>")
    parts.append("\t".join(f"<th>{escape(str(name))}</th>" for name in column_names))
    parts.append("</tr>")

    for row in rows:
        parts.append("<tr>")
        sprite_path = row[-1] if row[-1] else "sprites/0.png"
        sprite_html = (
            f'<td><img src="{escape(sprite_path)}" alt="sprite" '
            'style="height: 40px; width: 40px; object-fit: contain;"/></td>'
        )
        parts.append(sprite_html)
        parts.append("\t".join(f"<td>{escape(str(value))}</td>" for value in row[:-1]))
        parts.append("</tr>")

    parts.append("</table>")
    return "\n".join(parts)


def print_table(dbName, tableName, fileName):
    conn = sqlite3.connect(dbName)
    cursor = conn.cursor()

    rows = cursor.execute(
        "SELECT ROWID, name, points, games_played, winrate, kills, deaths, diff, KPG, "
        "COALESCE(path, 'sprites/0.png') as path FROM mons WHERE games_played > 500.0"
    ).fetchall()
    column_names = ["rowid", "name", "points", "games_played", "winrate", "kills", "deaths", "diff", "KPG"]
    conn.close()

    table_html = _build_table_html(column_names, rows)
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
    fileName = DB_ROOT / 'table.html'
    print_table(dbName, tableName, fileName)


if __name__ == "__main__":
    main()