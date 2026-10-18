from createDB import main as create_db_main
from replayScraper import main as replay_scraper_main
from table import main as table_main
from moveDB import main as move_db_main

def main():
    replay_scraper_main()
    create_db_main()
    table_main()
    move_db_main()

if __name__ == "__main__":
    main()