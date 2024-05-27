import torch
import torch.nn as nn
import torch.optim as optim
from environment import PokemonEnvironment, Pokemon, POKEMON_ENTRIES, MOVES
import numpy as np
import math
import random
from random_agent import RandomPlayer
import time
from tqdm import trange

class Model(nn.Module):
    def __init__(self, game, hidden_layers=3, hidden_dim=256):
        super().__init__()
        self.game = game

        self.input_layer = nn.Sequential(
            nn.Linear(game.state_dim, hidden_dim),
            nn.ReLU()
        )

        self.hidden_layers = nn.ModuleList()
        for _ in range(hidden_layers):
            self.hidden_layers.append(nn.Sequential(
                nn.Linear(hidden_dim, hidden_dim),
                nn.ReLU()
            ))

        self.policy_head = nn.Sequential(
            nn.Linear(hidden_dim, game.actions_dim),
            nn.Softmax(dim=-1)
        )

        self.value_head = nn.Sequential(
            nn.Linear(hidden_dim, 1),
            nn.Tanh()
        )
        
    def forward(self, x):
        x = self.input_layer(x)
        for layer in self.hidden_layers:
            x = layer(x)
        policy = self.policy_head(x)
        value = self.value_head(x)
        return policy, value

class Node:
    def __init__(self, game, args, state, active_pokemon, parent=None, action_taken=None, prior=0, battle=None):
        self.game = game
        self.args = args
        self.state = state
        self.parent = parent
        self.action_taken = action_taken
        self.prior = prior
        self.active_pokemon = active_pokemon
        self.battle = battle

        self.children = []

        self.value = 0
        self.visits = 0
        
    def is_full_expanded(self):
        return len(self.children) > 0
    
    def select(self):
        best_child = None
        best_ucb = -np.inf

        for child in self.children:
            ucb = self.get_ucb(child)
            if ucb > best_ucb:
                best_ucb = ucb
                best_child = child

        return best_child

    def get_ucb(self, child):
        if child.visits == 0:
            q_value = 0
        else:
            q_value = child.value / child.visits
        ucb = child.prior * math.sqrt(self.visits) / (1 + child.visits)
        return q_value + self.args["C"] * ucb
    
    def expand(self, self_policy, policies_for_other_mons, active_pokemon):
        # self_policy is a np array containing the policy for the current mon
        # policies_for_other_mons is a np arrays containing the policy for the other mons on the field relative to known information
        self_policy = self_policy
        team_pokemon_policy = policies_for_other_mons[0]
        opponent_1_policy = policies_for_other_mons[1]
        opponent_2_policy = policies_for_other_mons[2]
        for action1, prob1 in enumerate(self_policy):
            if prob1 == 0:
                continue
            for action2, prob2 in enumerate(team_pokemon_policy):
                if prob2 == 0:
                    continue
                for action3, prob3 in enumerate(opponent_1_policy):
                    if prob3 == 0:
                        continue
                    for action4, prob4 in enumerate(opponent_2_policy):
                        if prob4 == 0:
                            continue
                        child_state = self.state.copy()
                        child_state, child_battle_state = self.battle.get_next_battle_state(active_pokemon, (action1, action2, action3, action4))
                        self.children.append(Node(self.game, self.args, child_state, active_pokemon, self, action_taken=(action1, action2, action3, action4), prior=prob1 * prob2 * prob3 * prob4, battle=child_battle_state))
    
    def backpropagate(self, value):
        self.visits += 1
        self.value += value

        if self.parent is not None:
            self.parent.backpropagate(value)

# Only use MCTS for the battle phase        
class MonteCarloTreeSearch:
    def __init__(self, game, args, model):
        self.game = game
        self.args = args
        self.model = model

    @torch.no_grad()
    def search(self, state, active_pokemon):
        root = Node(self.game, self.args, state, active_pokemon, battle=self.game.battle)
        for search in range(self.args['num_searches']):
            node = root
            while node.is_full_expanded():
                node = node.select()

            value, is_terminal = self.game.battle.get_value_and_terminated(active_pokemon, node.action_taken)

            if not is_terminal:
                self_policy, value = self.model(
                    torch.tensor(node.state, dtype=torch.float32).unsqueeze(0)
                )
                team_pokemon_policy, _ = self.model(
                    torch.tensor(self.game.battle.get_team_state_from_active_pokemon(active_pokemon), dtype=torch.float32).unsqueeze(0)
                )
                opponent_1_policy, _ = self.model(
                    torch.tensor(self.game.battle.get_opponent_state_from_active_pokemon(active_pokemon, 0), dtype=torch.float32).unsqueeze(0)
                )
                opponent_2_policy, _ = self.model(
                    torch.tensor(self.game.battle.get_opponent_state_from_active_pokemon(active_pokemon, 1), dtype=torch.float32).unsqueeze(0)
                )
                self_policy = torch.softmax(self_policy, dim=-1).numpy().squeeze()#might be incorrect
                team_pokemon_policy = torch.softmax(team_pokemon_policy, dim=-1).numpy().squeeze()
                opponent_1_policy = torch.softmax(opponent_1_policy, dim=-1).numpy().squeeze()
                opponent_2_policy = torch.softmax(opponent_2_policy, dim=-1).numpy().squeeze()

                # Get valid actions then multiply policies by valid action corresponding to that mon
                self_valid_actions = self.game.battle.get_legal_action_space(active_pokemon)
                team_pokemon_valid_actions = self.game.battle.get_legal_action_space(active_pokemon, team_active_pokemon=True)
                opponent_1_valid_actions = self.game.battle.get_legal_action_space(active_pokemon, opposing_team_slots=0)
                opponent_2_valid_actions = self.game.battle.get_legal_action_space(active_pokemon, opposing_team_slots=1)

                self_policy = self_policy * self_valid_actions
                team_pokemon_policy = team_pokemon_policy * team_pokemon_valid_actions
                opponent_1_policy = opponent_1_policy * opponent_1_valid_actions
                opponent_2_policy = opponent_2_policy * opponent_2_valid_actions

                # Then normalize the policy
                self_policy = self_policy / np.sum(self_policy)
                team_pokemon_policy = team_pokemon_policy / np.sum(team_pokemon_policy)
                opponent_1_policy = opponent_1_policy / np.sum(opponent_1_policy)
                opponent_2_policy = opponent_2_policy / np.sum(opponent_2_policy)


                value = value.item()
                node.expand(self_policy, [team_pokemon_policy, opponent_1_policy, opponent_2_policy], active_pokemon)

            node.backpropagate(value)
                 
            
        action_probs = np.zeros(self.game.actions_dim)
        for child in root.children:
            action_probs[child.action_taken[0]] += child.visits
        action_probs = action_probs / np.sum(action_probs)
        return action_probs

class AlphaVGCZero:
    def __init__(self, model, optimizer, game, args):
        self.model = model
        self.optimizer = optimizer
        self.game = game
        self.args = args
        self.mcts = MonteCarloTreeSearch(game, args, model)
        self.team_pokemon = []
        self.team = []
        self.selected_pokemon = []
        self.wins = 0
        self.memory = None

    def __repr__(self):
        return "PokemonMasterAI PPO"

    def choose_pokemon(self):
        self.team_pokemon = random.sample(POKEMON_ENTRIES, 6)
        for p in self.team_pokemon:
            p = p[0]
            moveset = random.sample(p.moves, 4)
            moveset = [m.copy() for m in MOVES if m.name in moveset]
            self.team.append(Pokemon(p, moveset, self))

    def select_pokemon(self, opponent_pokemon):
        self.selected_pokemon = random.sample(self.team, 4)

    def choose_action(self, active_pokemon, available_actions):
        opposing_player = self.game.battle._get_opposing_player(self)
        battlefield = self.game.battle._get_battlefield_slots(self) + self.game.battle._get_battlefield_slots(opposing_player)
        if len(available_actions) == 0:
            return None
        all_switches = True
        #if battlefield[0] == None and battlefield[1] == None:
        #    exit()
        for a in available_actions:
            if a[0] != "switch":
                all_switches = False
                break
        if all_switches:
            #return random.choice(available_actions)
            if active_pokemon == None:
                state = self.game.battle.get_battle_state(self.selected_pokemon[0])
                legal_actions = self.game.battle.get_legal_action_space(self.selected_pokemon[0], action_type="switch")
            else:
                state = self.game.battle.get_battle_state(active_pokemon)
                legal_actions = self.game.battle.get_legal_action_space(active_pokemon, action_type="switch")
            switch_position = np.zeros(len(legal_actions))
            switch_position[72] = 1
            switch_position[73] = 1
            legal_switches = legal_actions*switch_position
                
            policy, _ = self.model(
                    torch.tensor(state, dtype=torch.float32).unsqueeze(0)
                )
            policy = torch.softmax(policy, dim=-1).detach().numpy().squeeze()
            policy = policy * legal_switches
            if np.sum(policy) == 0:
                return None
            policy = policy / np.sum(policy)
            action = np.random.choice(len(policy), p=policy)
            if self.memory is not None:
                self.memory.append((state, policy))
            return action

        else:
            state = self.game.battle.get_battle_state(active_pokemon)
            action_probs = self.mcts.search(state, active_pokemon=active_pokemon)
            action = np.random.choice(len(action_probs), p=action_probs)
            if self.memory is not None:
                self.memory.append((state, action_probs))
            
            return action

    def self_play(self):
        battles_per_self_play = self.args["num_battles_per_self_play"]
        p1 = self
        p2 = self.copy()
        p1.memory = []
        p2.memory = []
        p1.choose_pokemon()
        p2.choose_pokemon()
        for i in range(battles_per_self_play):
            p1.select_pokemon(p2.team)
            p2.select_pokemon(p1.team)
            self.game.run_battle(p1, p2)
        return_memory = []
        for state, policy in p1.memory:
            hist_outcome = p1.wins/battles_per_self_play if p1.wins > battles_per_self_play/2 else p1.wins/battles_per_self_play - 1
            return_memory.append((state, policy, hist_outcome))
        return return_memory                  
        
    def train(self, memory):
        random.shuffle(memory)
        for batchIDx in range(0, len(memory), self.args["batch_size"]):
            batch = memory[batchIDx:batchIDx+self.args["batch_size"]]
            states = torch.tensor([s for s, _, _ in batch], dtype=torch.float32)
            policies = torch.tensor([p for _, p, _ in batch], dtype=torch.float32)
            outcomes = torch.tensor([o for _, _, o in batch], dtype=torch.float32)
            self.optimizer.zero_grad()
            policy_preds, value_preds = self.model(states)
            policy_loss = -torch.sum(policies * torch.log(policy_preds)) # Maybe do cross entropy loss here
            value_loss = torch.sum((outcomes - value_preds.squeeze()) ** 2) # Maybe do MSE here
            loss = policy_loss + value_loss
            loss.backward()
            self.optimizer.step()

    def learn(self, save_path=None):
        for iteration in range(self.args["num_iterations"]):
            memory = []
            self.model.eval()
            for self_play_iteration in trange(self.args["num_self_play_iterations"]):
                memory += self.self_play()
            self.model.train()
            for epoch in trange(self.args["num_epochs"]):
                self.train(memory)
            torch.save(self.model.state_dict(), f"{save_path}/model_{iteration}.pt")
            torch.save(self.optimizer.state_dict(), f"{save_path}/optimizer_{iteration}.pt")

    def load_weights(self, filename):
        self.model.load_state_dict(torch.load(filename))

    def copy(self):
        return AlphaVGCZero(self.model, self.optimizer, self.game, self.args)

env = PokemonEnvironment()
model = Model(env)
optimizer = optim.Adam(model.parameters(), lr=0.001)
args = {
    "num_searches": 1000,
    "C": 0.8, # Exploitation vs exploration 0 is pure greed (exploitation), a high number is more exploration. we likely want to leand toward exploitation due to the branching factor of the game
    'num_iterations': 100,
    'num_self_play_iterations': 100,
    'num_battles_per_self_play': 20,
    'num_epochs': 4,
    'batch_size': 32
}
save_folder = "alphaVGC_zero_weights"
agent = AlphaVGCZero(model, optimizer, env, args)
agent.learn()