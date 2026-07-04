import pandas as pd
import numpy as np
from pathlib import Path

DB_ROOT = Path(__file__).resolve().parent.parent

def odds(player, wins, losses, diff, matchups, make_playoffs, file):

    # Current standings data
    teams_data = {
        'player': player,
        'wins': wins,
        'losses': losses,
        'diff': diff,
    }

    # Convert to DataFrame for easier manipulation
    standings_df = pd.DataFrame(teams_data).set_index('player')

    # All remaining matchups
    matchups = matchups  # List of tuples (team1, team2)

    # Initialize playoff counts for all teams
    playoff_counts_optimized = {team: 0 for team in standings_df.index}

    # Number of optimized simulations
    num_simulations_optimized = 10000  # Efficient simulation count

    # Function to simulate a scenario with variable diffs
    def simulate_scenario_with_variable_diff(outcomes, diffs):
        df = standings_df.copy()
        for i, outcome in enumerate(outcomes):
            team1, team2 = matchups[i]
            diff = diffs[i]
            if outcome == 0:
                df.at[team1, 'wins'] += 1
                df.at[team2, 'losses'] += 1
                df.at[team1, 'diff'] += diff
                df.at[team2, 'diff'] -= diff
            else:
                df.at[team2, 'wins'] += 1
                df.at[team1, 'losses'] += 1
                df.at[team2, 'diff'] += diff
                df.at[team1, 'diff'] -= diff
        df_sorted = df.sort_values(by=['wins', 'diff'], ascending=[False, False])
        return df_sorted.index[:make_playoffs]  # Top 8 teams

    # Run optimized simulations
    for _ in range(num_simulations_optimized):
        random_outcomes = np.random.randint(0, 2, len(matchups))
        random_diffs = np.random.randint(0, 7, len(matchups))
        
        top_8_teams = simulate_scenario_with_variable_diff(random_outcomes, random_diffs)
        
        for team in top_8_teams:
            playoff_counts_optimized[team] += 1

    # Calculate playoff odds
    playoff_odds_optimized = {team: count / num_simulations_optimized * 100 for team, count in playoff_counts_optimized.items()}

    # Convert results to DataFrame
    playoff_odds_optimized_df = pd.DataFrame({
        'team': playoff_odds_optimized.keys(),
        'playoff_odds (%)': playoff_odds_optimized.values()
    }).sort_values(by='playoff_odds (%)', ascending=False).reset_index(drop=True)

    with open(file, 'w') as f:
        playoff_odds_optimized_df.to_csv(f, index=False)

def main():
    # Example data
    player = ['Jamity Square', 'Arizona Heatwave', 'Baltiomore Rookidees', 'Consul of Regigigas', 'De Witt Diancies', 'Sunnyside Scream Tails', 'Metro Boomburstin', 'Alabama Feraligatrs', 'Boston Banettes', 'Prescott Pidgeots', 'We Ballin W Rocks', 'San Isidro Sinistchas', 'Edinburgh Enamorus', 'Washed Woopers']
    wins =   [6, 5, 5, 5, 4, 4, 4, 4, 3, 3, 3, 3, 2, 1]
    losses = [2, 2, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 6, 6]
    diff =   [7, 14, 6, 4, 7, 3, 3, 1, 1, -6, -6, -9, -12, -19]
    matchups = [
    ('San Isidro Sinistchas', 'Prescott Pidgeots'),
    ('Arizona Heatwave', 'Washed Woopers'),
    ('We Ballin W Rocks', 'Boston Banettes')]
    make_playoffs = 8
    file = DB_ROOT / "playoff_odds" / "odds.csv"

    odds(player, wins, losses, diff, matchups, make_playoffs, file)

if __name__ == "__main__":
    main()