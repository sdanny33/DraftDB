class Mon:
    def __init__(self, name):
        self.name = name
        self.kills = 0
        self.deaths = 0
        self.games_played = 0
        self.wins = 0
        self.nickname = ""
        self.moves = []
        self.item = ""
        self.ability = ""
        self.evs = [0, 0, 0, 0, 0, 0]
        self.nature = ""

    def increment_kills(self):
        self.kills += 1

    def increment_deaths(self): 
        self.deaths += 1

    def increment_games(self):
        self.games_played += 1

    def increment_wins(self):
        self.wins += 1
        
    def set_name(self, name):
        self.name = name

    def set_nickname(self, nickname):
        self.nickname = nickname

    def add_moves(self, moves):
        self.moves.extend(moves)

    def set_item(self, item):
        self.item = item

    def set_ability(self, ability):
        self.ability = ability

    def set_evs(self, evs):
        self.evs = evs

    def set_hp_ev(self, hp_ev):
        self.evs[0] = hp_ev

    def set_atk_ev(self, atk_ev):
        self.evs[1] = atk_ev

    def set_def_ev(self, def_ev):
        self.evs[2] = def_ev

    def set_spa_ev(self, spa_ev):
        self.evs[3] = spa_ev

    def set_spd_ev(self, spd_ev):
        self.evs[4] = spd_ev

    def set_spe_ev(self, spe_ev):
        self.evs[5] = spe_ev

    def set_nature(self, nature):
        self.nature = nature

    def print_stats(self):
        print(f"{self.name}: {self.kills} kills, {self.deaths} deaths, {self.games_played} games played, {self.wins} wins")

    def print_clear(self):
        print(f"{self.name}: {self.ability}, {self.item}, {self.moves}")

    def print_paste(self):
        moves = self.moves[:4]
        while len(moves) < 4:
            moves.append("Unseen Move")

        if self.item == "":
            self.item = "Unseen Item"
            
        print(
            f"{self.name} @ {self.item}\n"
            f"Ability: {self.ability}\n"
            f"EVs: {self.evs[0]} HP / {self.evs[1]} Atk / {self.evs[2]} Def / {self.evs[3]} SpA / {self.evs[4]} SpD / {self.evs[5]} Spe\n"
            f"{self.nature} Nature\n"
            f"- {moves[0]}\n"
            f"- {moves[1]}\n"
            f"- {moves[2]}\n"
            f"- {moves[3]}"
        )