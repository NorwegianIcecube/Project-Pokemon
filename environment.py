import random
import numpy as np
import numpy as np

STATE_DIM = 1000
ACTION_DIM = 91
BATTLES_PER_EPOCH = 100

class Pokemon:
    def __init__(self, pokemon, moves, trainer):
        self.pokemon = pokemon
        self.name = pokemon.name
        self.hp = pokemon.hp
        self.attack = pokemon.attack
        self.defense = pokemon.defense
        self.special_attack = pokemon.special_attack
        self.special_defense = pokemon.special_defense
        self.speed = pokemon.speed
        self.moves = moves
        self.status = []
        self.unique_status = None
        self.turns_asleep = 0
        self.protect_count = 0
        self.taunt_turns = 0
        self.helping_hand = False
        self.first_action_taken = False
        self.trainer = trainer
        self.player = None
        self.stats = {
            "hp": self.hp*2 + 110,
            "attack": self.attack*2 + 5,
            "defense": self.defense*2 + 5,
            "special_attack": self.special_attack*2 + 5,
            "special_defense": self.special_defense*2 + 5,
            "speed": self.speed*2 + 5
        }
        self.effective_stats = self.stats

    def poke_center(self):
        self.hp = self.pokemon.hp
        self.status = []
        self.unique_status = None
        for m in self.moves:
            m.pp = m.max_pp
        self._clear_stat_changes()

    def switch_reset(self):
        self.status = []
        self._clear_stat_changes()

    def _clear_stat_changes(self):
        self.effective_stats = self.stats

    def copy(self):
        pokemon = Pokemon(self.pokemon, [m.copy() for m in self.moves], self.trainer)
        pokemon.effective_stats = self.effective_stats.copy()
        pokemon.hp = self.hp
        pokemon.status = self.status.copy()
        pokemon.unique_status = self.unique_status
        pokemon.turns_asleep = self.turns_asleep
        pokemon.protect_count = self.protect_count
        pokemon.taunt_turns = self.taunt_turns
        pokemon.helping_hand = self.helping_hand
        pokemon.first_action_taken = self.first_action_taken
        for i, m in enumerate(pokemon.moves):
            m.pp = self.moves[i].pp
        return pokemon

    def __repr__(self):
        return self.name
    
    #def __eq__(self, other):
    #    if other == None:
    #        return False
    #    return self.name == other.name
    
    def __hash__(self):
        return hash(self.name)
    
    def __str__(self):
        return self.name

class PokemonEntry:
    def __init__(self, name, hp, attack, defense, special_attack, special_defense, speed, moves, type1, type2=None):
        self.name = name
        self.hp = hp
        self.attack = attack
        self.special_attack = special_attack
        self.defense = defense
        self.special_defense = special_defense
        self.speed = speed
        self.moves = moves
        self.type1 = type1
        self.type2 = type2

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        if other == None:
            return False
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        return self.name
    
class Move:
    def __init__(self, name, power, accuracy, type, move_type, pp, effect=None, priority=0, legal_targets="target"):
        self.name = name
        self.power = power
        self.accuracy = accuracy
        self.type = type
        self.move_type = move_type
        self.max_pp = pp
        self.pp = pp
        self.effect = effect
        self.priority = priority
        # Types of targets = ["target", "self", "all_adjacent", "all_opponents", "all_other", "all_adjacent_opponents", "all_adjacent_allies", "all_adjacent_other", "all_adjacent_opponents_other", "all_adjacent_allies_other", "all_adjacent_opponents_allies", "all_adjacent_opponents_allies_other"]
        self.legal_targets = legal_targets

    def copy(self):
        return Move(self.name, self.power, self.accuracy, self.type, self.move_type, self.pp, self.effect, self.priority, self.legal_targets)

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name+str(self.pp))

    def __str__(self):
        return self.name

# type chart
with open("chart.csv", "r") as f:
    chart = f.readlines()

types = chart[0].strip().split(",")[1:]
type_chart = {}
for line in chart[1:]:
    line = line.strip().split(",")
    type_chart[line[0]] = {types[i]: float(line[i+1]) for i in range(len(types))}

MOVES = [
    Move("Behemoth Blade", 100, 100, "Steel", "Physical", 5),
    Move("Play Rough", 90, 90, "Fairy", "Physical", 10),
    Move("Close Combat", 120, 100, "Fighting", "Physical", 5),
    Move("Iron Head", 80, 100, "Steel", "Physical", 15, effect=("flinch", 0.3)),
    Move("Sword Dance", 0, 100, "Normal", "Status", 20, effect=("attack", 2), legal_targets="self"),
    Move("Quick Attack", 40, 100, "Normal", "Physical", 30, priority=1),
    Move("Protect", 0, 100, "Normal", "Status", 10, effect=("protect"), legal_targets="self", priority=4),
    Move("Spore", 0, 100, "Grass", "Status", 15, effect=("sleep")),
    Move("Rage Powder", 0, 100, "Bug", "Status", 20, effect=("rage_powder"), legal_targets="self"),
    Move("Clear Smog", 50, 100, "Poison", "Special", 15),
    Move("Sludge Bomb", 90, 100, "Poison", "Special", 10, effect=("poison", 0.3)),
    Move("Giga Drain", 75, 100, "Grass", "Special", 10),
    Move("Fake Out", 40, 100, "Normal", "Physical", 10, effect=("flinch", 1), priority=3),
    Move("Flare Blitz", 120, 100, "Fire", "Physical", 15),
    Move("Darkest Lariat", 85, 100, "Dark", "Physical", 10),
    Move("U-turn", 70, 100, "Bug", "Physical", 20, effect=("switch")),
    Move("Parting Shot", 0, 100, "Dark", "Status", 20, effect=("multiple", ("attack", -1), ("special_attack", -1), ("switch") )),
    Move("Taunt", 0, 100, "Dark", "Status", 20, effect=("taunt")),
    Move("Nuzzle", 20, 100, "Electric", "Physical", 20, effect=("paralyze")),
    Move("Super Fang", 0, 90, "Normal", "Physical", 10, effect=("half_hp")),
    Move("Follow Me", 0, 100, "Normal", "Status", 20, effect=("follow_me"), legal_targets="self", priority=3),
    Move("Helping Hand", 0, 100, "Normal", "Status", 20, effect=("helping_hand"), legal_targets="all_adjacent_allies", priority=5),
    Move("Fake Tears", 0, 100, "Dark", "Status", 20, effect=("special_defense", -2)),
    Move("Thunder", 110, 70, "Electric", "Special", 10),
    Move("Thunderclap", 70, 100, "Electric", "Special", 5, priority=1),
    Move("Electroweb", 55, 95, "Electric", "Special", 15, effect=("speed", -1)),
    Move("Dragon Pulse", 85, 100, "Dragon", "Special", 10),
    Move("Snarl", 55, 95, "Dark", "Special", 15, effect=("attack", -1)),
    Move("Volt Switch", 70, 100, "Electric", "Special", 20, effect=("switch")),
    Move("Discharge", 80, 100, "Electric", "Special", 15),
    Move("Thunderbolt", 90, 100, "Electric", "Special", 15),
    Move("Weather Ball", 50, 100, "Normal", "Special", 10),
    Move("Hurricane", 110, 70, "Flying", "Special", 10),
    Move("Tailwind", 0, 100, "Flying", "Status", 15, effect=("tailwind"), legal_targets="self"),
    Move("U-turn-est", 70, 100, "Bug", "Physical", 20, effect=("switch")),
    Move("Wide Guard", 0, 100, "Rock", "Status", 10, effect=("wide_guard"), legal_targets="self", priority=3),
    Move("Surging Strikes", 25, 100, "Water", "Physical", 5, effect=("multiple_hits", 3)),
    Move("Aqua Jet", 40, 100, "Water", "Physical", 20, priority=1),
    Move("Ice Punch", 75, 100, "Ice", "Physical", 15, effect=("freeze", 0.1)),
    Move("Poison Jab", 80, 100, "Poison", "Physical", 20, effect=("poison", 0.3)),
    Move("Water Spout", 150, 100, "Water", "Special", 5),
    Move("Origin Pulse", 110, 85, "Water", "Special", 10),
    Move("Ice Beam", 90, 100, "Ice", "Special", 10),
    Move("Precipice Blades", 120, 85, "Ground", "Physical", 10),
    Move("Fire Punch", 75, 100, "Fire", "Physical", 15, effect=("burn", 0.1)),
    Move("Rock Slide", 75, 90, "Rock", "Physical", 10),
    Move("Thunder Punch", 75, 100, "Electric", "Physical", 15, effect=("paralyze", 0.1)),
    Move("Grassy Glide", 70, 100, "Grass", "Physical", 20, priority=1),
    Move("Wood Hammer", 120, 100, "Grass", "Physical", 10),
    Move("High Horsepower", 95, 95, "Ground", "Physical", 10),
    Move("Eruption", 150, 100, "Fire", "Special", 5),
    Move("Heat Wave", 95, 90, "Fire", "Special", 10),
    Move("Solar Beam", 120, 100, "Grass", "Special", 10),
    Move("Yawn", 0, 100, "Normal", "Status", 10, effect=("yawn")),
    Move("Trick Room", 0, 100, "Psychic", "Status", 5, effect=("trick_room"), legal_targets="self"),
    Move("Gyro Ball", 0, 100, "Steel", "Physical", 5),
    Move("Earthquake", 100, 100, "Ground", "Physical", 10, legal_targets="all_other"),
    Move("Safeguard", 0, 100, "Normal", "Status", 25, effect=("safeguard"), legal_targets="self"),
    Move("Ally Switch", 0, 100, "Psychic", "Status", 15, effect=("ally_switch"), legal_targets="self"),
    Move("Iron Defense", 0, 100, "Steel", "Status", 15, effect=("defense", 2), legal_targets="self"),
    Move("Body Press", 80, 100, "Fighting", "Physical", 10),

    # Struggle has to be last due to implementation of _get_legal_actions
    Move("Struggle", 50, 100, "Normal", "Physical", float("inf"))
]

zacian_crowned = PokemonEntry("Zacian", 92, 150, 115, 80, 115, 148, ["Behemoth Blade", "Play Rough", "Close Combat", "Iron Head", "Sword Dance", "Quick Attack", "Protect"], "Fairy", "Steel"),
amoonguss = PokemonEntry("Amoonguss", 114, 85, 70, 85, 80, 30, ["Spore", "Rage Powder", "Clear Smog", "Sludge Bomb", "Giga Drain", "Protect"], "Grass", "Poison"),
incineroar = PokemonEntry("Incineroar", 95, 115, 90, 80, 90, 60, ["Fake Out", "Flare Blitz", "Darkest Lariat", "Taunt", "U-turn", "Parting Shot", "Protect"], "Fire", "Dark"),
pachurisu = PokemonEntry("Pachurisu", 60, 45, 70, 45, 90, 95, ["Nuzzle", "Super Fang", "Follow Me", "Protect", "Helping Hand", "Fake Tears"], "Electric"),
raging_bolt = PokemonEntry("Raging Bolt", 125, 73, 91, 137, 89, 75, ["Thunder", "Thunderclap", "Electroweb", "Dragon Pulse", "Snarl", "Volt Switch", "Discharge", "Thunderbolt"], "Electric", "Dragon"),
pelipper = PokemonEntry("Pelipper", 60, 50, 100, 95, 70, 65, ["Weather Ball", "Hurricane", "Tailwind", "Protect", "U-turn", "Wide Guard"], "Water", "Flying"),
urshifu_rapid_strike = PokemonEntry("Urshifu", 100, 130, 100, 63, 60, 97, ["Surging Strikes", "Aqua Jet", "Close Combat", "Ice Punch", "Poison Jab", "Protect"], "Water", "Fighting"),
kyogre = PokemonEntry("Kyogre", 100, 100, 90, 150, 140, 90, ["Water Spout", "Origin Pulse", "Ice Beam", "Thunder", "Protect", "Wide Guard"], "Water"),
groudon = PokemonEntry("Groudon", 100, 150, 140, 100, 90, 90, ["Precipice Blades", "Fire Punch", "Rock Slide", "Thunder Punch", "Protect", "Wide Guard"], "Ground"),
rillaboom = PokemonEntry("Rillaboom", 100, 125, 90, 60, 70, 85, ["Grassy Glide", "Wood Hammer", "High Horsepower", "U-turn-est", "Protect"], "Grass"),
torkoal = PokemonEntry("Torkoal", 70, 85, 140, 85, 70, 20, ["Eruption", "Heat Wave", "Solar Beam", "Protect", "Yawn"], "Fire"),
bronzong = PokemonEntry("Bronzong", 67, 89, 116, 79, 116, 33, ["Trick Room", "Gyro Ball", "Earthquake", "Protect", "Safeguard", "Ally Switch", "Iron Defense", "Body Press"], "Steel", "Psychic"),

POKEMON_ENTRIES = [zacian_crowned, amoonguss, incineroar, pachurisu, raging_bolt, pelipper, urshifu_rapid_strike, kyogre, groudon, rillaboom, torkoal, bronzong]

class PokemonEnvironment:
    def __init__(self):
        self.battles_per_epoch = BATTLES_PER_EPOCH
        self.state_dim = STATE_DIM
        self.actions_dim = ACTION_DIM
        self.battle = None
    
    def get_choose_pokemon_state(self, action):
        return np.zeros(self.state_dim)
    
    def get_choose_action_state(self, action):
        return np.zeros(self.state_dim)
    
    def get_select_pokemon_state(self, action=None):
        return np.zeros(self.state_dim)

    def get_available_pokemon(self, selected_pokemon, pokemon_to_select_from=None):
        if pokemon_to_select_from == None:
            pokemon_to_select_from = POKEMON_ENTRIES
        return [p for p in pokemon_to_select_from if p not in selected_pokemon]
    
    def run_battle(self, player1, player2):
        self.battle = Battle(player1, player2)
        self.battle.run()
        winner = self.battle.winner
        self.battle = None
        return winner

class Battle:
    def __init__(self, player1, player2):
        self.is_simulation = False
        self.player1 = player1
        self.player2 = player2
        self.player_1_seen_moves = {}
        self.player_2_seen_moves = {}
        self.turn = 0
        self.winner = None
        self.p1_battlefield_slots = [self.player1.selected_pokemon[0], self.player1.selected_pokemon[1]]
        self.p2_battlefield_slots = [self.player2.selected_pokemon[0], self.player2.selected_pokemon[1]]
        self.player_1_seen_pokemon = [p.pokemon for p in self.player2.selected_pokemon]
        self.player_2_seen_pokemon = [p.pokemon for p in self.player1.selected_pokemon]
        self.player_1_seen_moves = {p: [] for p in self.player_1_seen_pokemon}
        self.player_2_seen_moves = {p: [] for p in self.player_2_seen_pokemon}
        self.trick_room = False
        self.trick_room_turns = 0

        self.log = [(0, "p1:switch", None, self.player1.selected_pokemon[0]), (0, "p1:switch", None, self.player2.selected_pokemon[0]), (0, "p2:switch", None, self.player1.selected_pokemon[1]), (0, "p2:switch", None, self.player2.selected_pokemon[1])]
        for p in self.player1.selected_pokemon:
            p.player = "p1"
        for p in self.player2.selected_pokemon:
            p.player = "p2"
        
    def run(self):
        #start_time = time.time()
        self.trick_room = False
        self.trick_room_turns = 0
        #log_printed = False
        while self.winner is None:
            self.turn += 1
            p1_action_1 = self.player1.choose_action(self.p1_battlefield_slots[0], self._get_legal_actions(self.player1, 0))
            if type(p1_action_1) == int:
                p1_action_1 = self._get_executable_action_from_index(p1_action_1, self.p1_battlefield_slots[0])
            p1_action_2 = self.player1.choose_action(self.p1_battlefield_slots[1], self._get_legal_actions(self.player1, 1))
            if type(p1_action_2) == int:
                p1_action_2 = self._get_executable_action_from_index(p1_action_2, self.p1_battlefield_slots[1])
            p2_action_1 = self.player2.choose_action(self.p2_battlefield_slots[0], self._get_legal_actions(self.player2, 0))
            if type(p2_action_1) == int:
                p2_action_1 = self._get_executable_action_from_index(p2_action_1, self.p2_battlefield_slots[0])
            p2_action_2 = self.player2.choose_action(self.p2_battlefield_slots[1], self._get_legal_actions(self.player2, 1))
            if type(p2_action_2) == int:
                p2_action_2 = self._get_executable_action_from_index(p2_action_2, self.p2_battlefield_slots[1])
                
            execute_order = self._order_actions(p1_action_1, p1_action_2, p2_action_1, p2_action_2)
            self._execute_actions(execute_order)
            self._end_of_round_effects()

            #self.printing = False
            #if time.time() - start_time > 10:
            #    self.printing = True

            #if self.printing and log_printed == False:
            #    print(self.log)
            #    log_printed = True

            #    print([(p, p.hp) for p in self.player1.selected_pokemon], [self.p1_battlefield_slots[0], self.p1_battlefield_slots[0].hp if self.p1_battlefield_slots[0] != None else None, self.p1_battlefield_slots[1], self.p1_battlefield_slots[1].hp if self.p1_battlefield_slots[1] != None else None])
            #    print([(p, p.hp) for p in self.player2.selected_pokemon], [self.p2_battlefield_slots[0], self.p2_battlefield_slots[0].hp if self.p2_battlefield_slots[0] != None else None, self.p2_battlefield_slots[1], self.p2_battlefield_slots[1].hp if self.p2_battlefield_slots[1] != None else None])
            #    print(execute_order)

            #if self.log != []:
            #    print(self.log)
            #    if self.log[0][0] > 100:
            #       print([(p, p.hp) for p in self.player1.selected_pokemon], [self.p1_battlefield_slots[0], self.p1_battlefield_slots[0].hp if self.p1_battlefield_slots[0] != None else None, self.p1_battlefield_slots[1], self.p1_battlefield_slots[1].hp if self.p1_battlefield_slots[1] != None else None])
            #       print([(p, p.hp) for p in self.player2.selected_pokemon], [self.p2_battlefield_slots[0], self.p2_battlefield_slots[0].hp if self.p2_battlefield_slots[0] != None else None, self.p2_battlefield_slots[1], self.p2_battlefield_slots[1].hp if self.p2_battlefield_slots[1] != None else None])
            #self.log = []

        if self.winner == self.player1:
            self.player1.wins += 1
        elif self.winner == self.player2:
            self.player2.wins += 1

        for p in self.player1.selected_pokemon:
            p.poke_center()
        for p in self.player2.selected_pokemon:
            p.poke_center()
        
        # Switch back out starting pokemon
        self.p1_battlefield_slots = [self.player1.selected_pokemon[0], self.player1.selected_pokemon[1]]
        self.p2_battlefield_slots = [self.player2.selected_pokemon[0], self.player2.selected_pokemon[1]]

    def get_value_and_terminated(self, active_pokemon, actions):
        if actions == None:
            return 0, False
        new_active_pokemon = active_pokemon.copy()
        active_player = active_pokemon.trainer
        battle_simulation = self.copy()
        team = battle_simulation._get_battlefield_slots(new_active_pokemon.trainer)
        team_pokemon = [p for p in team if p.name != new_active_pokemon.name][0].copy() if None not in team else None # CHANGED
        opposing_team = battle_simulation._get_battlefield_slots(battle_simulation._get_opposing_player(new_active_pokemon.trainer))
        opposing_pokemon_1 = opposing_team[0].copy() if opposing_team[0] != None else None
        opposing_pokemon_2 = opposing_team[1].copy() if opposing_team[1] != None else None
        new_actions = []
        for i, action in enumerate(actions):
            if type(action) == int:
                if i == 0:
                    active_mon = new_active_pokemon
                elif i == 1:
                    active_mon = team_pokemon
                elif i == 2:
                    active_mon = opposing_pokemon_1
                elif i == 3:
                    active_mon = opposing_pokemon_2
                action = battle_simulation._get_executable_action_from_index(action, active_mon)
            new_actions.append(action)
        actions = (new_actions[0], new_actions[1], new_actions[2], new_actions[3])
        actions = battle_simulation._order_actions(actions[0], actions[1], actions[2], actions[3])
        battle_simulation._execute_actions(actions)
        battle_simulation._end_of_round_effects()
        if battle_simulation.winner == None:
            return 0, False
        elif battle_simulation.winner == "draw":
            return 0, True
        elif battle_simulation.winner == self.player1 and active_player == self.player1:
            return 1, True
        elif battle_simulation.winner == self.player2 and active_player == self.player2:
            return 1, True
        elif battle_simulation.winner == self.player1 and active_player == self.player2:
            return -1, True
        elif battle_simulation.winner == self.player2 and active_player == self.player1:
            return -1, True

    def get_legal_action_space(self, active_pokemon, action_type=None, team_active_pokemon=None, opposing_team_slots=None):
        action_space = np.zeros(ACTION_DIM)
        
        if team_active_pokemon == True:
            active_team = self._get_battlefield_slots(active_pokemon.trainer)
            active_pokemon = active_team[0] if active_team[0] != active_pokemon else active_team[1]
        if opposing_team_slots == 0:
            opposing_player = self._get_opposing_player(active_pokemon.trainer)
            opposing_team = self._get_battlefield_slots(opposing_player)
            active_pokemon = opposing_team[0] if opposing_team[0] != None else None
        elif opposing_team_slots == 1:
            opposing_player = self._get_opposing_player(active_pokemon.trainer)
            opposing_team = self._get_battlefield_slots(opposing_player)
            active_pokemon = opposing_team[1] if opposing_team[1] != None else None

        if active_pokemon == None:
            action_space[-1] = 1
            return action_space
        elif active_pokemon.hp <= 0 and action_type != "switch":
            action_space[-1] = 1
            return action_space
        
        trainer = active_pokemon.trainer
        active_team = self._get_battlefield_slots(trainer)
        team_pokemon = [p for p in active_team if p.name != active_pokemon.name][0] if None not in active_team else None
        opposing_player = self._get_opposing_player(trainer)
        opposing_team = self._get_battlefield_slots(opposing_player)
        
        # first 72 indices are for moves and pokemon selection, irrelevant here
        a=0
        for i, p in enumerate(trainer.selected_pokemon):
            if p.hp > 0:
                if active_team[0] == None and active_team[1] == None:
                    action_space[72+a] = 1
                elif active_team[0] == None and active_team[1] != None:
                    if p.name != active_team[1].name:
                        action_space[72+a] = 1
                elif active_team[0] != None and active_team[1] == None:
                    if p.name != active_team[0].name:
                        action_space[72+a] = 1
                elif p.name != active_team[0].name and p.name != active_team[1].name:
                    action_space[72+a] = 1
                a+=1

        """
        action_space[72+a] = 1
                a+=1
        for i, p in enumerate(trainer.selected_pokemon):
            if p.hp > 0:
                if active_team[0] == None and active_team[1] == None:
                    legal_switches.append(p)
                elif active_team[0] == None and active_team[1] != None:
                    if p != active_team[1]:
                        legal_switches.append(p)
                elif active_team[0] != None and active_team[1] == None:
                    if p != active_team[0]:
                        legal_switches.append(p)
                elif p != active_team[0] and p != active_team[1]:
                    legal_switches.append(p)
        """

        if action_type == "switch":
            return action_space
        # index 72 and 73 are for switch actions (the 73rd and 74th actions)
        for i, m in enumerate(active_pokemon.moves):
            i*=4
            if m.pp == 0:
                continue
            if m.legal_targets == "target":
                if team_pokemon != None:
                    action_space[74+i] = 1
                if opposing_team[0] != None:
                    action_space[74+i+1] = 1
                if opposing_team[1] != None:
                    action_space[74+i+2] = 1
            elif m.legal_targets == "self" or m.legal_targets == "all_other" or m.legal_targets == "all_adjacent_allies":
                if m.legal_targets == "all_adjacent_allies" and team_pokemon == None:
                    continue
                action_space[74+i+3] = 1

        # if no other moves are available last index is true for struggle
        if np.sum(action_space) == 0:
            action_space[-2] = 1
        
        return action_space

    def get_battle_state(self, active_pokemon):
        state = np.zeros(STATE_DIM)
        current_node = 0
        active_team = self._get_battlefield_slots(active_pokemon.trainer)
        opposing_player = self._get_opposing_player(active_pokemon.trainer)
        opposing_team = self._get_battlefield_slots(opposing_player)
        
        max_stats = self._get_max_stats()
        
        # first 6*12*2 nodes are for pokemon on both teams
        team_pokemon = [active_pokemon]
        team_pokemon += [p for p in active_pokemon.trainer.team if p.name != active_pokemon.name]
        all_pokemon = team_pokemon + [p for p in opposing_player.team]
        for i, p in enumerate(all_pokemon):
            for pkmn in POKEMON_ENTRIES:
                state[current_node] = 1 if p.pokemon == pkmn[0] else 0
                current_node += 1

        # next 61*6 nodes are for moves that active player has on team
        for i, p in enumerate(team_pokemon):
            for move in MOVES:
                state[current_node] = 1 if move in p.moves else 0
                current_node += 1

        # next 6 nodes are for which pokemon have been selected for this battle
        for i, p in enumerate(team_pokemon):
            if p in active_pokemon.trainer.selected_pokemon:
                state[current_node] = 1
            current_node += 1

        # next 6 nodes are for which pokemon are known to be selected by opposing player
        for i, p in enumerate(opposing_player.team):
            if p.trainer == self.player2:
                if p in self.player_1_seen_pokemon:
                    state[current_node] = 1
            elif p.trainer == self.player1:
                if p in self.player_2_seen_pokemon:
                    state[current_node] = 1
            current_node += 1

        # next 61*4 nodes are for known move of opposing selected pokemon
        for i, p in enumerate(opposing_player.selected_pokemon):
            if p.trainer == self.player2:
                for move in MOVES:
                    if move in self.player_1_seen_moves[p]:
                        state[current_node] = 1
                    current_node += 1
            elif p.trainer == self.player1:
                for move in MOVES:
                    if move in self.player_2_seen_moves[p]:
                        state[current_node] = 1
                    current_node += 1

        # next 1 node for trick room
        state[current_node] = 1 if self.trick_room else 0
        current_node += 1

        on_battlefield = [active_pokemon]
        on_battlefield += [p for p in active_team if p.name != active_pokemon.name] if None not in active_team else [None]
        on_battlefield += [p for p in opposing_team]

        # next 4*4 nodes are for non-unique status effects on active pokemon (switched out mons lose status)
        for i, p in enumerate(on_battlefield):
            if p == None:
                current_node += 4
                continue
            state[current_node] = p.protect_count/5
            current_node += 1
            state[current_node] = 1 if p.status == "taunt" else 0
            current_node += 1
            state[current_node] = 1 if p.status == "yawn" else 0
            current_node += 1
            state[current_node] = 1 if p.first_action_taken else 0
            current_node += 1
        
        all_selected_pokemon = [active_pokemon]
        all_selected_pokemon += [p for p in active_pokemon.trainer.selected_pokemon if p.name != active_pokemon.name]
        all_selected_pokemon += [p for p in opposing_player.selected_pokemon]
        # next 6*8 nodes are for unique status effects on all selected pokemon
        for i, p in enumerate(all_selected_pokemon):
            if p.hp <= 0:
                current_node += 6
                continue
            state[current_node] = 1 if p.unique_status == "sleep" else 0
            current_node += 1
            state[current_node] = 1 if p.unique_status == "paralyze" else 0
            current_node += 1
            state[current_node] = 1 if p.unique_status == "freeze" else 0
            current_node += 1
            state[current_node] = p.turns_asleep/3
            current_node += 1
            state[current_node] = 1 if p.unique_status == "burn" else 0
            current_node += 1
            state[current_node] = 1 if p.unique_status == "poison" else 0
            current_node += 1

        # next 6*8 nodes are for current stats of all selected pokemon
        for i, p in enumerate(all_selected_pokemon):
            if p.trainer == self.player1 and active_pokemon.trainer == self.player1:
                if p not in self.player_1_seen_pokemon:
                    current_node += 6
                    continue
            elif p.trainer == self.player2 and active_pokemon.trainer == self.player2:
                if p not in self.player_2_seen_pokemon:
                    current_node += 6
                    continue
                
            if p.hp <= 0:
                current_node += 6
                continue
            state[current_node] = p.hp/max_stats["hp"]
            current_node += 1
            state[current_node] = p.effective_stats["attack"]/max_stats["attack"]
            current_node += 1
            state[current_node] = p.effective_stats["defense"]/max_stats["defense"]
            current_node += 1
            state[current_node] = p.effective_stats["special_attack"]/max_stats["special_attack"]
            current_node += 1
            state[current_node] = p.effective_stats["special_defense"]/max_stats["special_defense"]
            current_node += 1
            state[current_node] = p.effective_stats["speed"]/max_stats["speed"]
            current_node += 1

        return state

    def get_next_battle_state(self, active_pokemon, actions):
        new_active_pokemon = active_pokemon.copy()
        battle_simulation = self.copy()
        battle_simulation.is_simulation = True
        
        team = battle_simulation._get_battlefield_slots(new_active_pokemon.trainer)
        team_pokemon = [p for p in team if p.name != new_active_pokemon.name][0].copy() if None not in team else None
        opposing_team = battle_simulation._get_battlefield_slots(battle_simulation._get_opposing_player(new_active_pokemon.trainer))
        opposing_pokemon_1 = opposing_team[0].copy() if opposing_team[0] != None else None
        opposing_pokemon_2 = opposing_team[1].copy() if opposing_team[1] != None else None
        new_actions = []
        for i, action in enumerate(actions):
            if type(action) == int:
                if i == 0:
                    active_mon = new_active_pokemon
                elif i == 1:
                    active_mon = team_pokemon
                elif i == 2:
                    active_mon = opposing_pokemon_1
                elif i == 3:
                    active_mon = opposing_pokemon_2
                action = battle_simulation._get_executable_action_from_index(action, active_mon)
            new_actions.append(action)
        actions = (new_actions[0], new_actions[1], new_actions[2], new_actions[3])
        if actions[0] != None:
            if actions[0][0] == "move" and actions[0][2].pp == 0:
                print(actions)
        elif actions[1] != None:
            if actions[1][0] == "move" and actions[1][2].pp == 0:
                print(actions)
        elif actions[2] != None:
            if actions[2][0] == "move" and actions[2][2].pp == 0:
                print(actions)
        elif actions[3] != None:
            if actions[3][0] == "move" and actions[3][2].pp == 0:
                print(actions)
        for i, a1 in enumerate(actions):
            for j, a2 in enumerate(actions):
                if i != j and a1 != None and a2 != None:
                    if a1[0] == "move" and a2[0] == "move" and a1[1] == a2[1]:
                        print(actions)
        actions = battle_simulation._order_actions(actions[0], actions[1], actions[2], actions[3])
        battle_simulation._execute_actions(actions)
        battle_simulation._end_of_round_effects()
        next_state = battle_simulation.get_battle_state(new_active_pokemon)
        return next_state, battle_simulation

    def get_team_state_from_active_pokemon(self, active_pokemon):
        if active_pokemon == None:
            state = np.zeros(STATE_DIM)
            state[-1] = 1
            return state
        team = self._get_battlefield_slots(active_pokemon.trainer)
        team_pokemon = [p for p in team if p.name != active_pokemon.name][0] if None not in team else None
        if team_pokemon == None:
            state = np.zeros(STATE_DIM)
            state[-1] = 1
            return state
        state = self.get_battle_state(team_pokemon)
        return state
 
    def get_opponent_state_from_active_pokemon(self, active_pokemon, opponent_slot):
        state = np.zeros(STATE_DIM)
        opposing_battlefield_slots = self._get_battlefield_slots(self._get_opposing_player(active_pokemon.trainer))
        if opposing_battlefield_slots[opponent_slot] == None:
            state[-1] = 1
            return state
        active_opponent_pokemon = opposing_battlefield_slots[opponent_slot]

        if active_pokemon.trainer == self.player1:
            seen_pokemon = self.player_1_seen_pokemon
            seen_moves = self.player_1_seen_moves
            opponent_seen_pokemon = self.player_2_seen_pokemon
            opponent_seen_moves = self.player_2_seen_moves
        else:
            seen_pokemon = self.player_2_seen_pokemon
            seen_moves = self.player_2_seen_moves
            opponent_seen_pokemon = self.player_1_seen_pokemon
            opponent_seen_moves = self.player_1_seen_moves

        current_node = 0
        active_team = self._get_battlefield_slots(active_opponent_pokemon.trainer)
        opposing_player = self._get_opposing_player(active_opponent_pokemon.trainer)
        opposing_team = self._get_battlefield_slots(opposing_player)
        
        max_stats = self._get_max_stats()
        
        # first 6*12*2 nodes are for pokemon on both teams
        team_pokemon = [active_opponent_pokemon]
        team_pokemon += [p for p in active_opponent_pokemon.trainer.team if p.name != active_opponent_pokemon.name]
        all_pokemon = team_pokemon + [p for p in opposing_player.team]
        for i, p in enumerate(all_pokemon):
            for pkmn in POKEMON_ENTRIES:
                state[current_node] = 1 if p.pokemon == pkmn[0] else 0
                current_node += 1

        # next 60*6 nodes are for moves that active player has on team
        for i, p in enumerate(team_pokemon):
            for move in MOVES:
                if p not in seen_moves.keys():
                    current_node += 1
                    continue
                if move not in seen_moves[p]:
                    current_node += 1
                    continue
                state[current_node] = 1 if move in p.moves else 0
                current_node += 1

        # next 6 nodes are for which pokemon have been selected for this battle
        for i, p in enumerate(team_pokemon):
            if p in active_opponent_pokemon.trainer.selected_pokemon:
                if p not in seen_pokemon:
                    current_node += 1
                    continue
                state[current_node] = 1
            current_node += 1

        # next 6 nodes are for which pokemon are known to be selected by opposing player
        for i, p in enumerate(opposing_player.team):
            if p in opponent_seen_pokemon:
                state[current_node] = 1
            current_node += 1

        # next 60*4 nodes are for known move of opposing selected pokemon
        for i, p in enumerate(opposing_player.selected_pokemon):
            for move in MOVES:
                if p in opponent_seen_moves.keys():
                    if move in opponent_seen_moves[p]:
                        state[current_node] = 1
                current_node += 1


        # next 1 node for trick room
        state[current_node] = 1 if self.trick_room else 0
        current_node += 1

        on_battlefield = [active_opponent_pokemon]
        on_battlefield += [p for p in active_team if p.name != active_opponent_pokemon.name] if None not in active_team else [None]
        on_battlefield += [p for p in opposing_team]

        # next 4*4 nodes are for non-unique status effects on active pokemon (switched out mons lose status)
        for i, p in enumerate(on_battlefield):
            if p == None:
                current_node += 4
                continue
            state[current_node] = p.protect_count/5
            current_node += 1
            state[current_node] = 1 if p.status == "taunt" else 0
            current_node += 1
            state[current_node] = 1 if p.status == "yawn" else 0
            current_node += 1
            state[current_node] = 1 if p.first_action_taken else 0
            current_node += 1
        
        all_selected_pokemon = [active_opponent_pokemon]
        all_selected_pokemon += [p for p in active_opponent_pokemon.trainer.selected_pokemon if p.name != active_opponent_pokemon.name]
        all_selected_pokemon += [p for p in opposing_player.selected_pokemon]
        # next 6*8 nodes are for unique status effects on all selected pokemon
        for i, p in enumerate(all_selected_pokemon):
            if p.hp <= 0:
                current_node += 6
                continue
            state[current_node] = 1 if p.unique_status == "sleep" else 0
            current_node += 1
            state[current_node] = 1 if p.unique_status == "paralyze" else 0
            current_node += 1
            state[current_node] = 1 if p.unique_status == "freeze" else 0
            current_node += 1
            state[current_node] = p.turns_asleep/3
            current_node += 1
            state[current_node] = 1 if p.unique_status == "burn" else 0
            current_node += 1
            state[current_node] = 1 if p.unique_status == "poison" else 0
            current_node += 1

        # next 6*8 nodes are for current stats of all selected pokemon
        for i, p in enumerate(all_selected_pokemon):        
            if p not in opponent_seen_pokemon or p not in seen_pokemon:
                current_node += 6
                continue

            if p.hp <= 0:
                current_node += 6
                continue
            state[current_node] = p.hp/max_stats["hp"]
            current_node += 1
            state[current_node] = p.effective_stats["attack"]/max_stats["attack"]
            current_node += 1
            state[current_node] = p.effective_stats["defense"]/max_stats["defense"]
            current_node += 1
            state[current_node] = p.effective_stats["special_attack"]/max_stats["special_attack"]
            current_node += 1
            state[current_node] = p.effective_stats["special_defense"]/max_stats["special_defense"]
            current_node += 1
            state[current_node] = p.effective_stats["speed"]/max_stats["speed"]
            current_node += 1

        return state

    def _get_executable_action_from_index(self, action_index, active_pokemon):
        if active_pokemon == None:
            return None
        if action_index < 72:
            return None
        elif action_index == ACTION_DIM-1:
            return None
        elif action_index == ACTION_DIM-2:
            struggle_target = random.choice(self._get_battlefield_slots(self._get_opposing_player(active_pokemon.trainer)))
            if struggle_target == None:
                struggle_target = [p for p in self._get_battlefield_slots(self._get_opposing_player(active_pokemon.trainer)) if p != None][0]
            return ("move", active_pokemon, MOVES[-1], struggle_target)
        
            
        trainer = active_pokemon.trainer
        active_team = self._get_battlefield_slots(trainer)
        legal_switches = []
        for i, p in enumerate(trainer.selected_pokemon):
            if p.hp > 0:
                if active_team[0] == None and active_team[1] == None:
                    legal_switches.append(p)
                elif active_team[0] == None and active_team[1] != None:
                    if p.name != active_team[1].name:
                        legal_switches.append(p)
                elif active_team[0] != None and active_team[1] == None:
                    if p.name != active_team[0].name:
                        legal_switches.append(p)
                elif p.name != active_team[0].name and p.name != active_team[1].name:
                    legal_switches.append(p)
                
        if action_index == 72:
            return ("switch", active_pokemon, legal_switches[0])
        elif action_index == 73:
            if len(legal_switches) == 1:
                return ("switch", active_pokemon, legal_switches[0])
            elif len(legal_switches) == 2:
                return ("switch", active_pokemon, legal_switches[1])
            else:
                raise ValueError("No legal switches")
        action_index -= 74
        move_index = action_index//4
        target_index = action_index%4
        move = active_pokemon.moves[move_index]
        opposing_player = self._get_opposing_player(trainer)
        team_pokemon = [p for p in active_team if p.name != active_pokemon.name][0] if None not in active_team else None
        opposing_team = self._get_battlefield_slots(opposing_player)
        if move.legal_targets == "target":
            if target_index == 0:
                target = team_pokemon # Potential problem if target is None?
            elif target_index == 1:
                target = opposing_team[0]
            else:
                target = opposing_team[1]
        elif move.legal_targets == "self":
            target = active_pokemon
        elif move.legal_targets == "all_other":
            target = (team_pokemon, opposing_team[0], opposing_team[1])
        elif move.legal_targets == "all_adjacent_allies":
            target = team_pokemon

        return ("move", active_pokemon, move, target)

    def _get_legal_actions(self, player, pokemon_slot):
        actions = []
        battlefield_slots = self._get_battlefield_slots(player)
        if battlefield_slots[pokemon_slot] == None:
            return actions
        
        opposing_player = self._get_opposing_player(player)
        opposing_battlefield_slots = self._get_battlefield_slots(opposing_player)
        for m in battlefield_slots[pokemon_slot].moves:
            if m.pp == 0:
                continue
            if m.legal_targets == "target":
                if battlefield_slots[-1-pokemon_slot] != None:
                    actions.append(("move", battlefield_slots[pokemon_slot], m, battlefield_slots[-1-pokemon_slot]))
                if opposing_battlefield_slots[pokemon_slot] != None:
                    actions.append(("move", battlefield_slots[pokemon_slot], m, opposing_battlefield_slots[pokemon_slot]))
                if opposing_battlefield_slots[-1-pokemon_slot] != None:
                    actions.append(("move", battlefield_slots[pokemon_slot], m, opposing_battlefield_slots[-1-pokemon_slot]))
            elif m.legal_targets == "self":
                actions.append(("move", battlefield_slots[pokemon_slot], m, battlefield_slots[pokemon_slot]))
            elif m.legal_targets == "all_other":
                actions.append(("move", battlefield_slots[pokemon_slot], m, (battlefield_slots[-1-pokemon_slot], opposing_battlefield_slots[pokemon_slot], opposing_battlefield_slots[-1-pokemon_slot])))
            elif m.legal_targets == "all_adjacent_allies":
                if battlefield_slots[pokemon_slot-1] != None:
                    actions.append(("move", battlefield_slots[pokemon_slot], m, battlefield_slots[pokemon_slot-1]))
    
        if actions == []:
            # Struggle is a move
            if opposing_battlefield_slots[pokemon_slot] != None and opposing_battlefield_slots[-1-pokemon_slot] == None:
                actions.append(("move", battlefield_slots[pokemon_slot], MOVES[-1], opposing_battlefield_slots[pokemon_slot]))
            elif opposing_battlefield_slots[-1-pokemon_slot] != None and opposing_battlefield_slots[pokemon_slot] == None:
                actions.append(("move", battlefield_slots[pokemon_slot], MOVES[-1], opposing_battlefield_slots[-1-pokemon_slot]))
            else:
                actions.append(("move", battlefield_slots[pokemon_slot], MOVES[-1], opposing_battlefield_slots[random.choice([pokemon_slot, -1-pokemon_slot])]))

        # Get switch actions
        for p in player.selected_pokemon:
            if p.hp > 0 and p != battlefield_slots[0] and p != battlefield_slots[1]:
                actions.append(("switch", battlefield_slots[pokemon_slot], p))

        return actions
            
    def _get_max_stats(self):
        max_stats = {
            "hp": 0,
            "attack": 0,
            "defense": 0,
            "special_attack": 0,
            "special_defense": 0,
            "speed": 0
        }

        for p in POKEMON_ENTRIES:
            pkmn = p[0]
            if pkmn.hp > max_stats["hp"]:
                max_stats["hp"] = pkmn.hp
            if pkmn.attack > max_stats["attack"]:
                max_stats["attack"] = pkmn.attack
            if pkmn.defense > max_stats["defense"]:
                max_stats["defense"] = pkmn.defense
            if pkmn.special_attack > max_stats["special_attack"]:
                max_stats["special_attack"] = pkmn.special_attack
            if pkmn.special_defense > max_stats["special_defense"]:
                max_stats["special_defense"] = pkmn.special_defense
            if pkmn.speed > max_stats["speed"]:
                max_stats["speed"] = pkmn.speed

        return max_stats

    def _order_actions(self, p1_action_1, p1_action_2, p2_action_1, p2_action_2):
        actions = [p1_action_1, p1_action_2, p2_action_1, p2_action_2]
        switch_actions = []
        for i in range(4):
            if actions[i] == None:
                pass
            elif actions[i][0] == "switch":
                switch_actions.append(actions[i])
                actions[i] = None
        switch_actions = sorted(switch_actions, key=lambda x: x[1].speed, reverse=True)
        if self.trick_room:
            switch_actions = switch_actions[::-1]

        move_actions = []
        for i in range(4):
            if actions[i] == None:
                pass
            elif actions[i][0] == "move":
                move_actions.append(actions[i])
                actions[i] = None

        move_actions = sorted(move_actions, key=lambda x: (x[2].priority), reverse=True)
        temp_move_actions = []
        complete_move_actions = []

        last_priority = 100
        for m in move_actions:
            if m[2].priority < last_priority:
                if self.trick_room:
                    complete_move_actions += sorted(temp_move_actions, key=lambda x: x[1].speed)
                else:
                    complete_move_actions += sorted(temp_move_actions, key=lambda x: x[1].speed, reverse=True)
                temp_move_actions = []
                last_priority = m[2].priority
            temp_move_actions.append(m)
        if self.trick_room:
            complete_move_actions += sorted(temp_move_actions, key=lambda x: x[1].speed)
        else:
            complete_move_actions += sorted(temp_move_actions, key=lambda x: x[1].speed, reverse=True)
        
        actions = switch_actions + complete_move_actions
        return actions

    def _execute_actions(self, actions):
        for a in actions:      
            if a == None:
                pass
            elif a[0] == "move":
                self._execute_move(a[1], a[2], a[3])
            elif a[0] == "switch":
                self._execute_switch(a[1], a[2])

    def _execute_move(self, pokemon, move, target):
        if pokemon.hp <= 0:
            return
        active_player = pokemon.trainer
        if active_player == self.player2 and move not in self.player_1_seen_moves[pokemon]:
                    self.player_1_seen_moves[pokemon].append(move)
        elif active_player == self.player1 and move not in self.player_2_seen_moves[pokemon]:
                    self.player_2_seen_moves[pokemon].append(move)

        if type(target) != tuple and target != None:
            if target.hp <= 0:
                if target == self._get_battlefield_slots(target.trainer)[0]:
                    target = self._get_battlefield_slots(target.trainer)[1]
                else:
                    target = self._get_battlefield_slots(target.trainer)[0]

        if "taunt" in pokemon.status:
            pokemon.taunt_turns -= 1
            if pokemon.taunt_turns == 0:
                pokemon.status.remove("taunt")

        if pokemon.unique_status == "sleep":
            if random.random() < pokemon.turns_asleep/3:
                pokemon.unique_status = None
            pokemon.turns_asleep += 1
            return
        elif pokemon.unique_status == "paralyze":
            if random.random() < 0.25:
                return
        elif pokemon.unique_status == "freeze":
            if random.random() < 0.2:
                return
            pokemon.unique_status = None
        
        if "flinch" in pokemon.status:
            self.log.append((self.turn, f"{pokemon.player}:flinch", pokemon))
            pokemon.status.remove("flinch")
            pokemon.first_action_taken = True
            return

        if move.pp == 0:
            raise Exception(f"{move.name} has no PP but is being executed")
        
        if target == None:
            return

        move.pp -= 1
        if move.move_type == "Physical" or move.move_type == "Special":
            if type(target) == tuple:
                for t in target:
                    if t == None:
                        continue
                    damage = self._calculate_damage(pokemon, move, t)
                    if random.random() < move.accuracy:
                        t.hp -= damage
                        self.log.append((self.turn, f"{pokemon.player}:move", pokemon, move.name, t, damage, t.hp))
                    else:
                        self.log.append((self.turn, f"{pokemon.player}:miss", pokemon, move.name, t))
            else:
                damage = self._calculate_damage(pokemon, move, target)
                if random.random() < move.accuracy:
                    target.hp -= damage
                    self.log.append((self.turn, f"{pokemon.player}:move", pokemon, move.name, target, damage, target.hp))
                else:
                    self.log.append((self.turn, f"{pokemon.player}:miss", pokemon, move.name, target))


        elif move.move_type == "Status":
            if "taunt" in target.status:
                self.log.append((self.turn, f"{pokemon.player}:fail", pokemon, move.name))
                pokemon.first_action_taken = True
                return
            if move.effect[0] == "protect":
                if random.random() < (1/3)**pokemon.protect_count:
                    pokemon.status.append("protect")
                    pokemon.protect_count += 1
                    self.log.append((self.turn, f"{pokemon.player}:move", pokemon, move.name))
                else:
                    pokemon.protect_count = 0
                    self.log.append((self.turn, f"{pokemon.player}:fail", pokemon, move.name))
                
            elif move.effect[0] == "attack":
                if move.effect[1] > 0:
                    target.effective_stats["attack"]  = target.stats["attack"] * (2+move.effect[1])/2
                    target.effective_stats["attack"] = int(min(target.effective_stats["attack"], 4*target.attack))
                else:
                    target.effective_stats["attack"] = target.stats["attack"] * 2/(2-move.effect[1])
                    target.effective_stats["attack"] = int(max(target.effective_stats["attack"], 0.25*target.attack))
            elif move.effect[0] == "special_attack":
                if move.effect[1] > 0:
                    target.effective_stats["special_attack"] = target.stats["special_attack"] * (2+move.effect[1])/2
                    target.effective_stats["special_attack"] = int(min(target.effective_stats["special_attack"], 4*target.special_attack))
                else:
                    target.effective_stats["special_attack"] = target.stats["special_attack"] * 2/(2-move.effect[1])
                    target.effective_stats["special_attack"] = int(max(target.effective_stats["special_attack"], 0.25*target.special_attack))
            elif move.effect[0] == "defense":
                if move.effect[1] > 0:
                    target.effective_stats["defense"] = target.stats["defense"] * (2+move.effect[1])/2
                    target.effective_stats["defense"] = int(min(target.effective_stats["defense"], 4*target.defense))
                else:
                    target.effective_stats["defense"] = target.stats["defense"] * 2/(2-move.effect[1])
                    target.effective_stats["defense"] = int(max(target.effective_stats["defense"], 0.25*target.defense))
            elif move.effect[0] == "special_defense":
                if move.effect[1] > 0:
                    target.effective_stats["special_defense"] = target.stats["special_defense"] * (2+move.effect[1])/2
                    target.effective_stats["special_defense"] = int(min(target.effective_stats["special_defense"], 4*target.special_defense))
                else:
                    target.effective_stats["special_defense"] = target.stats["special_defense"] * 2/(2-move.effect[1])
                    target.effective_stats["special_defense"] = int(max(target.effective_stats["special_defense"], 0.25*target.special_defense))
            elif move.effect[0] == "speed":
                if move.effect[1] > 0:
                    target.effective_stats["speed"] = target.stats["speed"] * (2+move.effect[1])/2
                    target.effective_stats["speed"] = int(min(target.effective_stats["speed"], 4*target.speed))
                else:
                    target.effective_stats["speed"] = target.stats["speed"] * 2/(2-move.effect[1])
                    target.effective_stats["speed"] = int(max(target.effective_stats["speed"], 0.25*target.speed))
            elif move.effect[0] == "sleep":
                if target.unique_status == None:
                    target.unique_status = "sleep"
                    self.log.append((self.turn, f"{pokemon.player}:sleep", target))
            elif move.effect[0] == "rage_powder":
                pass
            elif move.effect[0] == "follow_me":
                pass
            elif move.effect[0] == "helping_hand":
                if self._get_battlefield_slots(pokemon.trainer)[0] == pokemon:
                    ally = self._get_battlefield_slots(pokemon.trainer)[1]
                    if ally != None:
                        ally.helping_hand = True
                else:
                    ally = self._get_battlefield_slots(pokemon.trainer)[0]
                    if ally != None:
                        ally.helping_hand = True
                self.log.append((self.turn, f"{pokemon.player}:move", pokemon, move.name, ally))
            elif move.effect[0] == "taunt":
                if "taunt" not in target.status:
                    target.status.append("taunt")
                    target.taunt_turns = 4
            elif move.effect[0] == "yawn":
                target.status.append("yawn")
            elif move.effect[0] == "trick_room":
                self.trick_room = True
                self.trick_room_turns = 5
            elif move.effect[0] == "wide_guard":
                pass
            elif move.effect[0] == "ally_switch":
                pass
            elif move.effect[0] == "tailwind":
                pass
            elif move.effect[0] == "safe_guard":
                pass
            elif move.effect[0] == "multiple":
                for e in move.effect[1:]:
                    if e[0] == "attack":
                        if e[1] > 0:
                            target.effective_stats["attack"]  = target.stats["attack"] * (2+e[1])/2
                            target.effective_stats["attack"] = int(min(target.effective_stats["attack"], 4*target.attack))
                        else:
                            target.effective_stats["attack"] = target.stats["attack"] * 2/(2-e[1])
                            target.effective_stats["attack"] = int(max(target.effective_stats["attack"], 0.25*target.attack))
                    elif e[0] == "special_attack":
                        if e[1] > 0:
                            target.effective_stats["special_attack"] = target.stats["special_attack"] * (2+e[1])/2
                            target.effective_stats["special_attack"] = int(min(target.effective_stats["special_attack"], 4*target.special_attack))
                        else:
                            target.effective_stats["special_attack"] = target.stats["special_attack"] * 2/(2-e[1])
                            target.effective_stats["special_attack"] = int(max(target.effective_stats["special_attack"], 0.25*target.special_attack))
                    elif e[0] == "switch":
                        if pokemon == self._get_battlefield_slots(pokemon.trainer)[0]:
                            active_slot = 0
                        else:
                            active_slot = 1
                        actions = self._get_legal_actions(pokemon.trainer, active_slot)
                        switch_actions = [a for a in actions if a[0] == "switch"]
                        switch = pokemon.trainer.choose_action(pokemon, switch_actions)
                        if type(switch) == int:
                            switch = self._get_executable_action_from_index(switch, pokemon)
                        self._execute_switch(pokemon, switch[2])
        pokemon.first_action_taken = True
        self._check_win()  

    def _execute_switch(self, pokemon, new_pokemon):
        battlefield_slots = self._get_battlefield_slots(pokemon.trainer)
        illegal_switch = self._check_switch_illegal(pokemon, new_pokemon)
        if illegal_switch:
            return
        
        active_player = pokemon.trainer
        if active_player == self.player2 and new_pokemon not in self.player_1_seen_pokemon:
            self.player_1_seen_pokemon.append(new_pokemon)
            self.player_1_seen_moves[new_pokemon] = []
        elif active_player == self.player1 and new_pokemon not in self.player_2_seen_pokemon:
            self.player_2_seen_pokemon.append(new_pokemon)
            self.player_2_seen_moves[new_pokemon] = []

        for i in range(2):
            if battlefield_slots[i] == pokemon:
                battlefield_slots[i] = new_pokemon
                break
        pokemon.switch_reset()
        self.log.append((self.turn, f"{pokemon.player}:switch", pokemon, new_pokemon))

    def _check_switch_illegal(self, pokemon, new_pokemon):
        if pokemon == None:
            return True
        if new_pokemon == None:
            return False
        if new_pokemon.hp <= 0:
            return True
        if new_pokemon == self._get_battlefield_slots(new_pokemon.trainer)[0] or new_pokemon == self._get_battlefield_slots(new_pokemon.trainer)[1]:
           return True
        return False

    def _calculate_damage(self, attacker, move, defender):
        # Accuracy check
        if defender == None:
            return 0
        if random.random() > move.accuracy:
            return 0
        if move.name == "Fake Out":
            if attacker.first_action_taken:
                return 0
        if move.effect != None:
            if move.effect[0] == "flinch":
                if random.random() < move.effect[1]:
                    defender.status.append("flinch")
            if move.effect[0] == "paralyze" and defender.unique_status == None:
                if random.random() < move.effect[1]:
                    defender.unique_status = "paralyze"
                    self.log.append((self.turn, f"{defender.player}:paralyze", defender))
            if move.effect[0] == "poison" and defender.unique_status == None:
                if random.random() < move.effect[1]:
                    defender.unique_status = "poison"
                    self.log.append((self.turn, f"{defender.player}:poison", defender))
            if move.effect[0] == "burn" and defender.unique_status == None:
                if random.random() < move.effect[1]:
                    defender.unique_status = "burn"
                    self.log.append((self.turn, f"{defender.player}:burn", defender))
            if move.effect[0] == "freeze" and defender.unique_status == None:
                if random.random() < move.effect[1]:
                    defender.unique_status = "freeze"
                    self.log.append((self.turn, f"{defender.player}:freeze", defender))
            if move.effect[0] == "half_hp":
                return defender.hp//2


        if move.move_type == "Physical":
            attack = attacker.stats["attack"]
            defense = defender.stats["defense"]

        elif move.move_type == "Special":
            attack = attacker.stats["special_attack"]
            defense = defender.stats["special_defense"]

        else:
            raise Exception("Move type not recognized")
        
        if move.type == attacker.pokemon.type1 or move.type == attacker.pokemon.type2:
            stab = 1.5
        else:
            stab = 1
        
        type_effectiveness = 1
        type_effectiveness *= type_chart[move.type][defender.pokemon.type1]
        if defender.pokemon.type2 != None:
            type_effectiveness *= type_chart[move.type][defender.pokemon.type2]
        
        if attacker.unique_status == "burn" and move.move_type == "Physical":
            burn = 0.5
        else:
            burn = 1

        if attacker.helping_hand:
            helping_hand = 1.5
        else:
            helping_hand = 1

        damage = ((22*move.power*(attack/defense))/50 + 2)*stab*type_effectiveness*(random.randint(85, 100)/100)*burn*helping_hand
        attacker.helping_hand = False

        if move.effect != None:
            if move.effect[0] == "multiple_hits":
                for i in range(move.effect[1]):
                    if random.random() > move.accuracy:
                        continue
                    damage += ((22*move.power*(attack/defense))/50 + 2)*stab*type_effectiveness*(random.randint(85, 100)/100)

            if move.effect[0] == "switch":
                if attacker == self._get_battlefield_slots(attacker.trainer)[0]:
                    active_slot = 0
                else:
                    active_slot = 1
                    
                actions = self._get_legal_actions(attacker.trainer, active_slot)
                switch_actions = [a for a in actions if a[0] == "switch"]
                switch = attacker.trainer.choose_action(attacker, switch_actions)
                if type(switch) == int:
                    switch = self._get_executable_action_from_index(switch, attacker)
                
                if switch != None:
                    self._execute_switch(attacker, switch[2])

        if move == MOVES[-1]:
            attacker.hp -= attacker.pokemon.hp//4
        if damage < 0:
            raise Exception("Damage less than 0")
        return int(damage)

    def _get_opposing_player(self, player):
        if player == self.player1:
            return self.player2
        else:
            return self.player1

    def _get_battlefield_slots(self, player):
        if player == self.player1:
            return self.p1_battlefield_slots
        else:
            return self.p2_battlefield_slots

    def _check_win(self):
        p1_win = True
        p2_win = True
        for p in self.player1.selected_pokemon:
            if p.hp > 0:
                p2_win = False
        for p in self.player2.selected_pokemon:
            if p.hp > 0:
                p1_win = False

        if p1_win and p2_win:
            self.winner = "draw"
        elif p1_win:
            self.winner = self.player1
        elif p2_win:
            self.winner = self.player2

    def copy(self):
        new_battle = Battle(self.player1, self.player2)
        new_battle.turn = self.turn
        new_battle.winner = self.winner
        new_battle.p1_battlefield_slots = [p.copy() if p != None else None for p in self.p1_battlefield_slots]
        new_battle.p2_battlefield_slots = [p.copy() if p != None else None for p in self.p2_battlefield_slots]
        new_battle.log = self.log.copy()
        return new_battle

    def _end_of_round_effects(self):
        for battlefield_side in [self.p1_battlefield_slots, self.p2_battlefield_slots]:
            for p in battlefield_side:
                if p == None:
                    continue
                if p.unique_status == "burn":
                    p.hp -= p.pokemon.hp//16
                    self.log.append((self.turn, f"{p.player}:burn", p, p.hp))
                if p.unique_status == "poison":
                    p.hp -= p.pokemon.hp//8
                    self.log.append((self.turn, f"{p.player}:poison", p, p.hp))
                if "yawn" in p.status:
                    p.status.remove("yawn")
                    p.unique_status = "sleep"
                    self.log.append((self.turn, f"{p.player}:pkmn_fell_asleep", p))
                if "helping_hand" in p.status:
                    p.status.remove("helping_hand")

        self._check_win()
        if self.is_simulation:
            return
        for battlefield_side in [self.p1_battlefield_slots, self.p2_battlefield_slots]:
            for active_slot, p in enumerate(battlefield_side):
                if p == None:
                    continue
                #    trainer = 
                #    actions = self._get_legal_actions(trainer, active_slot)
                #    switch_actions = [a for a in actions if a[0] == "switch"]
                #    switch = trainer.choose_action(None, switch_actions)
                #    if switch != None:
                #        self._execute_switch(p, switch[2])
                #    else:
                #        continue
                if p.hp <= 0:
                    actions = self._get_legal_actions(p.trainer, active_slot)
                    switch_actions = [a for a in actions if a[0] == "switch"]
                    switch = p.trainer.choose_action(p, switch_actions)
                    if type(switch) == int:
                        switch = self._get_executable_action_from_index(switch, p)
                    if switch != None:
                        self._execute_switch(p, switch[2])                      
                    else:
                        self._execute_switch(p, None)
                

        if self.trick_room:
            self.trick_room_turns -= 1
            if self.trick_room_turns == 0:
                self.trick_room = False

        