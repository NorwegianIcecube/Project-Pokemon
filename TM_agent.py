import random
import numpy as np
import pandas as pd
from environment import Pokemon, POKEMON_ENTRIES, MOVES, STATE_DIM, PokemonEnvironment
from random_agent import RandomPlayer
import pickle
from tqdm import trange
from random_agent import RandomPlayer


class TsetlinMachine:
    def __init__(self, num_features, num_clauses, states):

        self.num_features = num_features
        self.num_clauses = num_clauses
        self.states = states
        # Each clause is represented as two lists of states for each literal and its negation
        self.clauses = [
            {'include': [states // 2] * num_features * 2, 'exclude': [states // 2] * num_features * 2}
            for _ in range(num_clauses)
        ]

    def predict(self, features):
        vote = 0
        for clause in self.clauses:
            clause_value = True
            for i in range(self.num_features * 2):  # Features and their negations
                literal = features[i // 2] if i % 2 == 0 else 1 - features[i // 2]
                if clause['include'][i] > clause['exclude'][i] and literal == 0:
                    clause_value = False
                    break
            vote += 1 if clause_value else 0
        return vote >= (self.num_clauses // 2)

    def update(self, features, target):
        for clause in self.clauses:
            for i in range(self.num_features * 2):
                literal = features[i // 2] if i % 2 == 0 else 1 - features[i // 2]
                if target == 1:  # Type I Feedback
                    if literal == 1:
                        clause['include'][i] = max(1, clause['include'][i] - 1)
                        clause['exclude'][i] = min(self.states, clause['exclude'][i] + 1)
                    else:
                        clause['exclude'][i] = max(1, clause['exclude'][i] - 1)
                        clause['include'][i] = min(self.states, clause['include'][i] + 1)
                else:  # Type II Feedback
                    if literal == 0:
                        clause['include'][i] = min(self.states, clause['include'][i] + 1)
                        clause['exclude'][i] = max(1, clause['exclude'][i] - 1)

    def load_weights(self, weights):
        self.clauses = weights['clauses']

class PokemonMasterAI:

    def __init__(self, gameenv, weights=None):
        self.tm = TsetlinMachine(num_features=STATE_DIM, num_clauses=100, states=10)
        if weights:
            self.tm.load_weights(weights)
        self.team_pokemon = []
        self.team = []
        self.selected_pokemon = []
        self.wins = 0
        self.gameenv = gameenv
        self.states_from_battles = []  # List to store states from each battle

    def __repr__(self):
        return "Tsetlin Machine AI"
    
    def binarize_features(self, state):
        base_state = state[:-48]  # All features except the last 48
        continuous_stats = state[-48:]  # Last 48 features to be binarized
        thresholds = [0.25, 0.5, 0.75]
        binary_stats = []

        for stat in continuous_stats:
            for threshold in thresholds:
                binary_stats.append(1 if stat > threshold else 0)

        # Combine the original part of the state with the new binary features
        return np.concatenate((base_state, binary_stats))

    def choose_pokemon(self):
        # Random selection for the first round
        self.team_pokemon = random.sample(POKEMON_ENTRIES, 6)
        for entry in self.team_pokemon:
            entry = entry[0]
            moveset = random.sample(entry.moves, 4)
            moveset = [m.copy() for m in MOVES if m.name in moveset]
            self.team.append(Pokemon(entry, moveset, self))

    def select_pokemon(self, opponent_pokemon):
        self.selected_pokemon = random.sample(self.team, 4)

    def choose_action(self, active_pokemon, available_actions):
        if len(available_actions) == 0:
            return None
        state = self.gameenv.battle.get_battle_state(active_pokemon)
        state = self.binarize_features(state)
        self.states_from_battles.append(state)  # Append state with a placeholder for the reward
        predictions = [self.tm.predict(state) for action in available_actions]
        best_action_index = np.argmax(predictions)
        return available_actions[best_action_index]

    def train(self, win_percentage, battles_per_epoch):
        reward = 1 if win_percentage > 0.5 else 0
        for state in self.states_from_battles:
            #print(state)
            #print(len(state))
            self.tm.update(state, reward)
        self.states_from_battles.clear()  # Clear after learning

    def save_weights(self, filename):
        try:
            with open(filename, 'wb') as f:
                pickle.dump({
                    'clauses': self.tm.clauses,
                    'num_features': self.tm.num_features,
                    'num_clauses': self.tm.num_clauses,
                    'states': self.tm.states
                }, f)
            print(f"Weights saved to {filename}")
        except Exception as e:
            print(f"Failed to save weights: {e}")
    
def load_weights(filename):
    with open(filename, 'rb') as f:
        data = pickle.load(f)
    return data


weights = load_weights('weights99.pkl')

env = PokemonEnvironment()
player1 = PokemonMasterAI(env, weights)
player2 = RandomPlayer()

EPOCHS = 100
BATTLES_PER_EPOCH = 80

total_p1_wins = 0
total_p2_wins = 0

for e in range(EPOCHS):  
    player1.team = []
    player2.team = []
    player1.choose_pokemon()
    player2.choose_pokemon()

    battle_logs = []
    for i in trange(BATTLES_PER_EPOCH):#//2):
        #print(i)
        player1.select_pokemon(player2.team)
        player2.select_pokemon(player1.team)

        winner = env.run_battle(player1, player2)
        if winner == player1:
            player1.wins += 1
        elif winner == player2:
            player2.wins += 1

    print(f"Epoch {e+1}/{EPOCHS} - p1Wins: {player1.wins}")
    print(f"Epoch {e+1}/{EPOCHS} - p2Wins: {player2.wins}")

    total_p1_wins += player1.wins
    total_p2_wins += player2.wins

    win_percentage = player1.wins / BATTLES_PER_EPOCH
    win_percentage = player2.wins / BATTLES_PER_EPOCH

    player1.train(win_percentage, BATTLES_PER_EPOCH)
    player2.train(win_percentage, BATTLES_PER_EPOCH)

    player1.save_weights(f"weights{e}.pkl")

print(f"p1 win percentage: {total_p1_wins / (EPOCHS * BATTLES_PER_EPOCH)}")
print(f"p2 win percentage: {total_p2_wins / (EPOCHS * BATTLES_PER_EPOCH)}")

