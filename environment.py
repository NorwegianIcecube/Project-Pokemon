import random
import numpy as np
import time

class Battle:
    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2
        self.turn = 0
        self.winner = None
        self.p1_battlefield_slots = [self.player1.selected_pokemon[0], self.player1.selected_pokemon[1]]
        self.p2_battlefield_slots = [self.player2.selected_pokemon[0], self.player2.selected_pokemon[1]]
        self.log = [(0, "p1:switch", None, self.player1.selected_pokemon[0]), (0, "p1:switch", None, self.player2.selected_pokemon[0]), (0, "p2:switch", None, self.player1.selected_pokemon[1]), (0, "p2:switch", None, self.player2.selected_pokemon[1])]
        for p in self.player1.selected_pokemon:
            p.player = "p1"
        for p in self.player2.selected_pokemon:
            p.player = "p2"
        

    def run(self):
        start_time = time.time()
        self.trick_room = False
        self.trick_room_turns = 0
        log_printed = False
        while self.winner is None:
            self.turn += 1
            p1_action_1 = self.player1.choose_action(self.log, self._get_legal_actions(self.player1, 0))
            p1_action_2 = self.player1.choose_action(self.log, self._get_legal_actions(self.player1, 1))
            p2_action_1 = self.player2.choose_action(self.log, self._get_legal_actions(self.player2, 0))
            p2_action_2 = self.player2.choose_action(self.log, self._get_legal_actions(self.player2, 1))
                
            execute_order = self._order_actions(p1_action_1, p1_action_2, p2_action_1, p2_action_2)
            self._execute_actions(execute_order)
            self._end_of_round_effects()

            self.printing = False
            if time.time() - start_time > 10:
                self.printing = True

            if self.printing and log_printed == False:
                print(self.log)
                log_printed = True

            #if self.printing:
                print([(p, p.hp) for p in self.player1.selected_pokemon], [self.p1_battlefield_slots[0], self.p1_battlefield_slots[0].hp if self.p1_battlefield_slots[0] != None else None, self.p1_battlefield_slots[1], self.p1_battlefield_slots[1].hp if self.p1_battlefield_slots[1] != None else None])
                print([(p, p.hp) for p in self.player2.selected_pokemon], [self.p2_battlefield_slots[0], self.p2_battlefield_slots[0].hp if self.p2_battlefield_slots[0] != None else None, self.p2_battlefield_slots[1], self.p2_battlefield_slots[1].hp if self.p2_battlefield_slots[1] != None else None])
                print(execute_order)

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

    def _get_legal_actions(self, player, pokemon_slot):
        actions = []
        battlfefield_slots = self._get_battlefield_slots(player)
        if battlfefield_slots[pokemon_slot] == None:
            return actions
        
        opposing_player = self._get_opposing_player(player)
        opposing_battlfefield_slots = self._get_battlefield_slots(opposing_player)
        for m in battlfefield_slots[pokemon_slot].moves:
            if m.pp == 0:
                continue
            if m.legal_targets == "target":
                if battlfefield_slots[-1-pokemon_slot] != None:
                    actions.append(("move", battlfefield_slots[pokemon_slot], m, battlfefield_slots[-1-pokemon_slot]))
                if opposing_battlfefield_slots[pokemon_slot] != None:
                    actions.append(("move", battlfefield_slots[pokemon_slot], m, opposing_battlfefield_slots[pokemon_slot]))
                if opposing_battlfefield_slots[-1-pokemon_slot] != None:
                    actions.append(("move", battlfefield_slots[pokemon_slot], m, opposing_battlfefield_slots[-1-pokemon_slot]))
            elif m.legal_targets == "self":
                actions.append(("move", battlfefield_slots[pokemon_slot], m, battlfefield_slots[pokemon_slot]))
            elif m.legal_targets == "all_other":
                actions.append(("move", battlfefield_slots[pokemon_slot], m, (battlfefield_slots[-1-pokemon_slot], opposing_battlfefield_slots[pokemon_slot], opposing_battlfefield_slots[-1-pokemon_slot])))
            elif m.legal_targets == "all_adjacent_allies":
                if battlfefield_slots[pokemon_slot-1] != None:
                    actions.append(("move", battlfefield_slots[pokemon_slot], m, battlfefield_slots[pokemon_slot-1]))
    
        if actions == []:
            # Struggle is a move
            if opposing_battlfefield_slots[pokemon_slot] != None:
                actions.append(("move", battlfefield_slots[pokemon_slot], moves[-1], opposing_battlfefield_slots[pokemon_slot]))
            if opposing_battlfefield_slots[-1-pokemon_slot] != None:
                actions.append(("move", battlfefield_slots[pokemon_slot], moves[-1], opposing_battlfefield_slots[-1-pokemon_slot]))

        # Get switch actions
        for p in player.selected_pokemon:
            if p.hp > 0 and p != battlfefield_slots[0] and p != battlfefield_slots[1]:
                actions.append(("switch", battlfefield_slots[pokemon_slot], p))

        return actions

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
                        self._execute_switch(pokemon, target)
        pokemon.first_action_taken = True
        self._check_win()  

    def _execute_switch(self, pokemon, new_pokemon):
        battlefield_slots = self._get_battlefield_slots(pokemon.trainer)
        illegal_switch = self._check_switch_illegal(pokemon, new_pokemon)
        if illegal_switch:
            return
        
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
                switch = attacker.trainer.choose_action(self.log, switch_actions)
                if switch != None:
                    self._execute_switch(attacker, switch[2])

        if move == moves[-1]:
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

        self._check_win()

        for battlefield_side in [self.p1_battlefield_slots, self.p2_battlefield_slots]:
            for active_slot, p in enumerate(battlefield_side):
                if p == None:
                    trainer = self.player1 if battlefield_side == self.p1_battlefield_slots else self.player2
                    actions = self._get_legal_actions(trainer, active_slot)
                    switch_actions = [a for a in actions if a[0] == "switch"]
                    switch = trainer.choose_action(self.log, switch_actions)
                    if switch != None:
                        self._execute_switch(p, switch[2])
                    else:
                        continue
                if p.hp <= 0:
                    actions = self._get_legal_actions(p.trainer, active_slot)
                    switch_actions = [a for a in actions if a[0] == "switch"]
                    switch = p.trainer.choose_action(self.log, switch_actions)
                    if switch != None:
                        self._execute_switch(p, switch[2])                      
                    else:
                        self._execute_switch(p, None)
                

        if self.trick_room:
            self.trick_room_turns -= 1
            if self.trick_room_turns == 0:
                self.trick_room = False

        

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
        return Pokemon(self.pokemon, [m.copy() for m in self.moves], self.trainer)

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
        return hash(self.name)

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

moves = [
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
    Move("U-turn", 70, 100, "Bug", "Physical", 20, effect=("switch")),
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
rillaboom = PokemonEntry("Rillaboom", 100, 125, 90, 60, 70, 85, ["Grassy Glide", "Wood Hammer", "High Horsepower", "U-turn", "Protect"], "Grass"),
torkoal = PokemonEntry("Torkoal", 70, 85, 140, 85, 70, 20, ["Eruption", "Heat Wave", "Solar Beam", "Protect", "Yawn"], "Fire"),
bronzong = PokemonEntry("Bronzong", 67, 89, 116, 79, 116, 33, ["Trick Room", "Gyro Ball", "Earthquake", "Protect", "Safeguard", "Ally Switch", "Iron Defense", "Body Press"], "Steel", "Psychic"),

pokemon_entries = [zacian_crowned, amoonguss, incineroar, pachurisu, raging_bolt, pelipper, urshifu_rapid_strike, kyogre, groudon, rillaboom, torkoal, bronzong]
