import random
from environment import Pokemon, POKEMON_ENTRIES, MOVES

class RandomPlayer:
    def __init__(self):
        self.team_pokemon = []
        self.team = []
        self.selected_pokemon = []
        self.wins = 0

    def __repr__(self):
        return "RandomPlayer"

    def choose_pokemon(self):
        self.team_pokemon = random.sample(pokemon_entries, 6)
        for p in self.team_pokemon:
            p = p[0]
            moveset = random.sample(p.moves, 4)
            moveset = [m.copy() for m in moves if m.name in moveset]
            self.team.append(Pokemon(p, moveset, self))

    def select_pokemon(self, opponent_pokemon):
        self.selected_pokemon = random.sample(self.team, 4)

    def choose_action(self, battle_log, available_actions):
        if len(available_actions) == 0:
            return None
        return random.choice(available_actions)

    def train(self, logs):
        # do something
        self.wins = 0
        pass

    def save_weights(self, filename):
        pass