import pandas as pd
import numpy as np

def odds(player, wins, losses, diff, matchups, make_playoffs):

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
        random_diffs = np.random.randint(1, 3, len(matchups))
        
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

    print(playoff_odds_optimized_df)

def main():
    # Example data
    player = ['Johning Johners', 'Krooked Kingdom', 'Skull and Bones', 'Phoenix Ho-Ohs', 'Double Trouble', 'Dos Sweepers', 'Carcinogang', 'The Phantom Typhlosion', 'New York Latios', 'Emogla Gaming']
    wins =   [8, 8, 8, 7, 7, 7, 6, 6, 6, 6]
    losses = [6, 6, 6, 7, 7, 8, 8, 8, 8, 9]
    diff =   [14, 12, 3, -2, -4, -4, 1, -8, -11, -13]
    matchups = [
            ('Skull and Bones', 'Krooked Kingdom'),
    ('Dos Sweepers', 'Emogla Gaming'),
    ('Carcinogang', 'Johning Johners'),
    ('Double Trouble', 'The Phantom Typhlosion'),
    ('New York Latios', 'Phoenix Ho-Ohs'),
    ('Skull and Bones', 'Krooked Kingdom'),
    ('Carcinogang', 'Johning Johners'),
    ('Double Trouble', 'The Phantom Typhlosion'),
    ('New York Latios', 'Phoenix Ho-Ohs'),
    ]
    make_playoffs = 6

    odds(player, wins, losses, diff, matchups, make_playoffs)

if __name__ == "__main__":
    main()