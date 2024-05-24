import random
from environment import Pokemon, pokemon_entries, moves

class SelectBestMoveAgent:
    def __init__(self):
        self.team_pokemon = []
        self.team = []
        self.selected_pokemon = []
        self.wins = 0

    def __repr__(self):
        return "Select Best Move Agent"

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

        best_move = None
        move_power = -1
        switches = []
        for action in available_actions:
            if action[0] == "move":
                if type(action[3]) == tuple:
                    new_move_power = action[2].power
                    if new_move_power > move_power:
                        best_move = action
                        move_power = new_move_power
                    elif best_move is None:
                        best_move = action
                elif action[1].trainer != action[3].trainer or action[1] == action[3]:
                    new_move_power = action[2].power
                    if new_move_power > move_power:
                        best_move = action
                        move_power = new_move_power
                    elif best_move is None:
                        best_move = action
            elif action[0] == "switch":
                switches.append(action)

        if best_move is not None:         
            return best_move
        elif len(switches) > 0:
            return random.choice(switches)
        else:
            return None

    def train(self, logs, battles_per_epoch):
        # do something
        self.wins = 0
        pass

    def save_weights(self, filename):
        pass