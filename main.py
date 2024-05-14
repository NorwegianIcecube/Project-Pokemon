import random
import numpy as np
import pickle
#import shap
from environment import Battle
from pokemon_master_AI import PokemonMasterAI
from random_agent import RandomPlayer

player1 = PokemonMasterAI()
player2 = RandomPlayer()

EPOCHS = 1000
BATTLES_PER_EPOCH = 1000

total_p1_wins = 0
total_p2_wins = 0
for e in range(EPOCHS):    
    player1.choose_pokemon()
    player2.choose_pokemon()

    battle_logs = []
    for i in range(BATTLES_PER_EPOCH):#//2):
        #print(e, i)
        player1.select_pokemon(player2.team)
        player2.select_pokemon(player1.team)
        battle = Battle(player1, player2)
        battle.run()

        battle_logs.append(battle.log)

    print(f"Epoch {e+1}/{EPOCHS} - p1Wins: {player1.wins}")
    print(f"Epoch {e+1}/{EPOCHS} - p2Wins: {player2.wins}")

    total_p1_wins += player1.wins
    total_p2_wins += player2.wins

    player1.train(battle_logs, BATTLES_PER_EPOCH)
    player2.train(battle_logs, BATTLES_PER_EPOCH)

print(f"p1 win percentage: {total_p1_wins / (EPOCHS * BATTLES_PER_EPOCH)}")
print(f"p2 win percentage: {total_p2_wins / (EPOCHS * BATTLES_PER_EPOCH)}")

player1.save_weights("weights1.pkl")
player2.save_weights("weights2.pkl")