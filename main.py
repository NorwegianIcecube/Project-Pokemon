import random
import numpy as np
import pickle
import torch
import torch.optim as optim
from environment import PokemonEnvironment
from tqdm import trange

from pokemon_master_AI import PokemonMasterAI
from random_agent import RandomPlayer
from best_move_enemy_target import SelectBestMoveAgent
from AlphaVGC_Zero import AlphaVGCZero, Model

EPOCHS = 10
BATTLES_PER_EPOCH = 10

env = PokemonEnvironment()

model = Model(env)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
optimizer = optim.Adam(model.parameters(), lr=0.001)
args = {
        "num_searches": 5,
        "C": 0.5,
        'num_iterations': 1,
        'num_self_play_iterations': 1,
        'num_battles_per_self_play': 1,
        'num_epochs': 5,
        'batch_size': 32
    }
player1 = AlphaVGCZero(model=model, optimizer=optimizer, game=env, args=args, device=device)
player1.load_weights("model_2.pt")
#player1 = SelectBestMoveAgent()
player2 = RandomPlayer()

for e in trange(EPOCHS):
    player1.choose_pokemon()
    player2.choose_pokemon()

    battle_logs = []
    for i in trange(BATTLES_PER_EPOCH):#//2):
        #print(e, i)
        player1.select_pokemon(player2.team)
        player2.select_pokemon(player1.team)
        winner = env.run_battle(player1, player2)
        #print(f"Winner: {winner}")
        
        #if winner == player1:
        #    player1.wins += 1
        #elif winner == player2:
        #    player2.wins += 1

    #print(f"Epoch {e+1}/{EPOCHS} - p1Wins: {player1.wins}")
    #print(f"Epoch {e+1}/{EPOCHS} - p2Wins: {player2.wins}")

    #total_p1_wins += player1.wins
    #total_p2_wins += player2.wins

print(f"p1 win percentage: {player1.wins / (EPOCHS * BATTLES_PER_EPOCH)}")
print(f"p2 win percentage: {player2.wins / (EPOCHS * BATTLES_PER_EPOCH)}")