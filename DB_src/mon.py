import populateInfo

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
        self.evs = {
            "hp": 0,
            "atk": 0,
            "def": 0,
            "spa": 0,
            "spd": 0,
            "spe": 0
        }
        self.nature = ""
        self.base_stats = {
            "hp": 0,
            "atk": 0,
            "def": 0,
            "spa": 0,
            "spd": 0,
            "spe": 0
        }
        self.type = []
        self.level = 100  # Default level
        self.current_hp = 100  # Default current HP
        self.alive = True  # Default alive status
        self.boosts = {
            "atk": 0,
            "def": 0,
            "spa": 0,
            "spd": 0,
            "spe": 0,
            "accuracy": 0,
            "evasion": 0
        }
        self.damage = {}
        self.set_base_stats(populateInfo.get_base_stats(name))
        self.set_type(populateInfo.get_types(name))
        self.set_ability(populateInfo.get_abilities(name))
        self.set_evs(populateInfo.get_evs(name))
        self.set_nature(populateInfo.get_nature(name))

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
        self.evs = {
            "hp": evs.get("hp", 0),
            "atk": evs.get("atk", 0),
            "def": evs.get("def", 0),
            "spa": evs.get("spa", 0),
            "spd": evs.get("spd", 0),
            "spe": evs.get("spe", 0)
        }

    def set_nature(self, nature):
        self.nature = nature

    def set_base_stats(self, base_stats):
        self.base_stats = base_stats

    def get_evs(self):
        return self.evs

    def reset_evs(self):
        self.evs = {
            "hp": 0,
            "atk": 0,
            "def": 0,
            "spa": 0,
            "spd": 0,
            "spe": 0
        }

    def get_base_stats(self):
        return self.base_stats

    def set_type(self, types):
        self.type = types

    def set_level(self, level):
        self.level = level

    def get_types(self):
        return self.type

    def get_level(self):
        return self.level

    def get_nature(self):
        return self.nature

    def set_current_hp(self, hp):
        self.current_hp = hp
        if self.current_hp <= 0:
            self.alive = False

    def get_current_hp(self):
        return self.current_hp

    def set_boosts(self, boosts):
        self.boosts = boosts

    def get_boosts(self):
        return self.boosts
        
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
            f"EVs: {self.evs['hp']} HP / {self.evs['atk']} Atk / {self.evs['def']} Def / {self.evs['spa']} SpA / {self.evs['spd']} SpD / {self.evs['spe']} Spe\n"
            f"{self.nature} Nature\n"
            f"- {moves[0]}\n"
            f"- {moves[1]}\n"
            f"- {moves[2]}\n"
            f"- {moves[3]}"
        )