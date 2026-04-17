import sqlite3
from pathlib import Path

DB_ROOT = Path(__file__).resolve().parent.parent

def populate_sprite_paths(dbName):
    """Populate sprite paths for all Pokemon in the database."""
    conn = sqlite3.connect(dbName)
    cursor = conn.cursor()
    
    # Check if path column exists
    cursor.execute("PRAGMA table_info(mons)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'path' not in columns:
        print("Adding 'path' column to mons table...")
        cursor.execute('ALTER TABLE mons ADD COLUMN path TEXT DEFAULT NULL')
    
    sprite_dir = DB_ROOT / 'sprites'
    
    # Get all Pokemon
    cursor.execute('SELECT id FROM mons')
    pokemon_ids = [row[0] for row in cursor.fetchall()]
    
    for pokemon_id in pokemon_ids:
        sprite_file = sprite_dir / f'{int(pokemon_id)}.png'
        
        # Use the specific sprite if it exists, otherwise default to 0.png
        if sprite_file.exists():
            # Store relative path from project root
            sprite_path = 'sprites/' + str(int(pokemon_id)) + '.png'
        else:
            sprite_path = 'sprites/0.png'
        
        cursor.execute('UPDATE mons SET path = ? WHERE id = ?', (sprite_path, pokemon_id))
    
    conn.commit()
    conn.close()
    print(f"Updated sprite paths for {len(pokemon_ids)} Pokemon")

if __name__ == "__main__":
    dbName = DB_ROOT / 'database' / 'monDB.sqlite'
    populate_sprite_paths(dbName)
