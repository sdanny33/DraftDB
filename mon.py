class Mon:
    kills = 0
    deaths = 0
    games_played = 0
    wins = 0
    nickname = ""

    def __init__(self, name):
        self.name = name

    def increment_kills(self):
        self.kills += 1

    def increment_deaths(self): 
        self.deaths += 1

    def increment_games(self):
        self.games_played += 1

    def increment_wins(self):
        self.wins += 1
        
    def set_nickname(self, nickname):
        self.nickname = nickname

    def print_stats(self):
        print(f"{self.name}: {self.kills} kills, {self.deaths} deaths, {self.games_played} games played, {self.wins} wins")