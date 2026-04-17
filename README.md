# DraftDB

## Author

Daniel Soares. Email me if you have any questions (dcs3personal@gmail.com).

## Description

Stat tracking database for Pokémon Draft. The database contains matches from my own draft league, Smogon tournaments, and saved replays from the Pokémon Showdown server dating as far back as I could access.

## Database

The replay scraper scrapes the saved draft replays from the Pokémon Showdown server. The create DB command initially creates the database and updates the statistics using the methods outlined in the parser. To update the database, simply run the main function. To create your own database, update the methods in createDB and replayScraper, respectively.

## Teams

The team’s portion of the project extracts given pokepastes to get the raw data for each mon. The data include the mon's name, items, abilities, EVs, nature, and moves.

## Website

A GitHub page that displays the database in table form. Clicking the top of a column sorts that column. If a mon is not present, it's likely because they have fewer than 500 games logged in the database.
