import csv
from bs4 import BeautifulSoup
import requests
import pandas
from pathlib import Path

DB_ROOT = Path(__file__).resolve().parent.parent
def format():
    path = DB_ROOT / 'teams' /"output.csv"
    output_path = DB_ROOT / 'teams' / "teams.csv"
    
    # Read all lines from the file
    with open(path, 'r') as f:
        lines = [line.rstrip('\n') for line in f.readlines()]
    
    # Group every 8 rows into chunks and write as columns
    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f)
        for i in range(0, len(lines), 9):
            chunk = lines[i:i+9]

            while len(chunk) < 9:
                chunk.append('')
            writer.writerow(chunk)

def main():
    format()

if __name__ == "__main__":
    main()

