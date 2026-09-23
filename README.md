# DraftDB

DraftDB is a Pokémon Draft replay database and statistics website. It collects Pokémon Showdown Gen 9 Draft replays, parses battle events, and turns them into per-Pokémon performance statistics.

The dataset combines replays from my own draft league, Smogon tournaments, and publicly available Pokémon Showdown replays. Statistics are currently shown for Pokémon with more than 500 recorded games on the main leaderboard.

## Website

The frontend is a React and Vite app deployed to GitHub Pages.

- **Battle Stats**: sortable leaderboard with sprites, points, games played, win rate, kills, deaths, kill differential, damage, damage taken, and switches.
- **Mon Lookup**: search for a Pokémon to view its Pokédex number, typing, sprite, base-stat chart, and draft performance cards.
- **Home**: project landing page and navigation.

Run the website locally:

```powershell
cd my-react-app
npm install
npm run dev
```

Create a production build with `npm run build`, or preview the build with `npm run preview`. GitHub Pages deployment is handled by `.github/workflows/deploy.yml`.

## Database Pipeline

The Python pipeline in `DB_src` updates the replay cache and statistics database:

1. `replayScraper.py` finds recent Gen 9 Draft replay URLs from Pokémon Showdown.
2. `replaySaver.py` downloads and caches replay logs in `database/`.
3. `parser.py` extracts battle events and updates Pokémon statistics.
4. `createDB.py` calculates derived values such as win rate, KPG, average damage, and average switches.
5. `table.py` exports the database data used by the website.

Run the full update from the database source directory:

```powershell
cd DB_src
python main.py
```

The pipeline expects network access to Pokémon Showdown and writes to `DB_CSV/` and `database/`. Existing replay IDs are tracked so repeated runs process only new replays.

## Supporting Tools

- `paste/` parses Pokémon Showdown Poképastes, including items, abilities, EVs, natures, and moves.
- `teams/` contains team scraping and formatting utilities.
- `playoff_odds/` contains draft playoff odds calculations.
- `sprites/` stores Pokémon sprite assets used by the database and website.

## Project Layout

```text
DB_CSV/          Replay URL archives and source Pokémon data
DB_src/          Scraping, replay caching, parsing, and database updates
database/        SQLite databases and cached replay data
my-react-app/    React/Vite website
paste/           Poképaste parsing tools
playoff_odds/    Playoff odds scripts and data
sprites/         Pokémon sprite assets
teams/           Team scraping and formatting tools
```

## Author

Daniel Soares. Questions and feedback: dcs3personal@gmail.com.
