import sqlite3
from html import escape
from pathlib import Path
import re

DB_ROOT = Path(__file__).resolve().parent.parent

GENERATED_START = "<!-- GENERATED_TABLE_START -->"
GENERATED_END = "<!-- GENERATED_TABLE_END -->"


def _build_table_html(column_names, rows):
    parts = ["<table>", "<tr>"]
    parts.append("\t".join(f"<th>{escape(str(name))}</th>" for name in column_names))
    parts.append("</tr>")

    for row in rows:
        parts.append("<tr>")
        parts.append("\t".join(f"<td>{escape(str(value))}</td>" for value in row))
        parts.append("</tr>")

    parts.append("</table>")
    return "\n".join(parts)


def _inject_into_intro(html_content, table_html):
    generated_block = f"{GENERATED_START}\n{table_html}\n{GENERATED_END}"

    # Replace existing generated content if present.
    if GENERATED_START in html_content and GENERATED_END in html_content:
        pattern = re.compile(
            rf"{re.escape(GENERATED_START)}.*?{re.escape(GENERATED_END)}",
            re.DOTALL,
        )
        return pattern.sub(generated_block, html_content, count=1)

    intro_opening_div = re.search(
        r'<div[^>]*class=["\'][^"\']*\bintro\b[^"\']*["\'][^>]*>',
        html_content,
        flags=re.IGNORECASE,
    )
    if not intro_opening_div:
        return None

    insert_at = intro_opening_div.end()
    return (
        html_content[:insert_at]
        + "\n"
        + generated_block
        + "\n"
        + html_content[insert_at:]
    )

def print_table(dbName, tableName, fileName):
    conn = sqlite3.connect(dbName)
    cursor = conn.cursor()

    # Fetch all rows from the specified table.
    cursor.execute(f"SELECT * FROM {tableName}")
    rows = cursor.execute("SELECT ROWID, name, points, games_played, winrate, kills, deaths, diff FROM mons WHERE games_played > 0.0").fetchall()
    column_names = [description[0] for description in cursor.description]
    conn.close()

    table_html = _build_table_html(column_names, rows)

    output_path = Path(fileName)
    if output_path.exists() and output_path.suffix.lower() == ".html":
        html_content = output_path.read_text(encoding="utf-8")
        updated_html = _inject_into_intro(html_content, table_html)
        if updated_html is not None:
            output_path.write_text(updated_html, encoding="utf-8")
            return

def main():
    dbName = DB_ROOT / 'database' / 'monDB.sqlite'
    tableName = 'mons'
    fileName = DB_ROOT / 'index.html'
    print_table(dbName, tableName, fileName)

if __name__ == "__main__":
    main()