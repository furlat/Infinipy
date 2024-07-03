from dataclasses import dataclass, field
import random
from infinipy.dnd.statsblock import StatsBlock, ActionEconomy, Attack, Damage, Dice, DamageType, AttackType, AdvantageStatus, ActionType,Action,StatusEffect
from infinipy.dnd.battlemap import BattleMap
from infinipy.dnd.monsters.goblin import create_goblin
from infinipy.dnd.monsters.skeleton import create_skeleton
from pydantic import BaseModel, Field
from typing import List, Dict, Tuple, Optional
from enum import Enum

class ActionCost(BaseModel):
    action: int = 0
    bonus_action: int = 0
    reaction: int = 0
    movement: int = 0

class ActionOutcome(BaseModel):
    success_probability: float
    expected_damage: float
    expected_healing: float
    status_effects: List[StatusEffect] = Field(default_factory=list)

class ActionOption(BaseModel):
    action: Action
    target: Optional[str]  # Target's ID, None for self-targeted actions
    cost: ActionCost
    outcome: ActionOutcome

class DecisionStrategy(str, Enum):
    RANDOM = "random"
    AGGRESSIVE = "aggressive"
    DEFENSIVE = "defensive"
    SUPPORTIVE = "supportive"

class Actor(BaseModel):
    stats_block: StatsBlock
    strategy: DecisionStrategy = DecisionStrategy.RANDOM

    def get_available_actions(self, combat_manager: 'CombatManager') -> List[ActionOption]:
        available_actions = []
        for action in self.stats_block.actions:
            if isinstance(action, Attack):
                targets = combat_manager.get_valid_targets(self.stats_block.id, action.name)
                for target_id in targets:
                    cost = self._calculate_action_cost(action)
                    outcome = self._calculate_action_outcome(action, target_id, combat_manager)
                    available_actions.append(ActionOption(action=action, target=target_id, cost=cost, outcome=outcome))
            else:
                # Handle non-attack actions (e.g., Dodge, Dash, etc.)
                cost = self._calculate_action_cost(action)
                outcome = self._calculate_action_outcome(action, None, combat_manager)
                available_actions.append(ActionOption(action=action, target=None, cost=cost, outcome=outcome))
        
        return available_actions

    def _calculate_action_cost(self, action: Action) -> ActionCost:
        cost = ActionCost()
        for action_cost in action.cost:
            if action_cost.type == ActionType.ACTION:
                cost.action += action_cost.cost
            elif action_cost.type == ActionType.BONUS_ACTION:
                cost.bonus_action += action_cost.cost
            elif action_cost.type == ActionType.REACTION:
                cost.reaction += action_cost.cost
            elif action_cost.type == ActionType.MOVEMENT:
                cost.movement += action_cost.cost
        return cost

    def _calculate_action_outcome(self, action: Action, target_id: Optional[str], combat_manager: 'CombatManager') -> ActionOutcome:
        if isinstance(action, Attack):
            target = combat_manager.creatures[target_id] if target_id else None
            hit_probability = self._calculate_hit_probability(action, target, combat_manager)
            expected_damage = hit_probability * action.average_damage
            return ActionOutcome(success_probability=hit_probability, expected_damage=expected_damage, expected_healing=0)
        else:
            # Handle non-attack actions
            return ActionOutcome(success_probability=1.0, expected_damage=0, expected_healing=0)

    def _calculate_hit_probability(self, attack: Attack, target: StatsBlock, combat_manager: 'CombatManager') -> float:
        attacker_pos = combat_manager.battle_map.get_creature_position(self.stats_block.id)
        target_pos = combat_manager.battle_map.get_creature_position(target.id)
        
        is_threatened = combat_manager.battle_map.is_threatened(self.stats_block.id)
        is_ranged_attack = attack.attack_type in [AttackType.RANGED_WEAPON, AttackType.RANGED_SPELL]
        
        advantage_status = AdvantageStatus.DISADVANTAGE if (is_threatened and is_ranged_attack) else AdvantageStatus.NONE
        
        if advantage_status == AdvantageStatus.ADVANTAGE:
            hit_chance = 1 - (target.armor_class - attack.hit_bonus - 1) ** 2 / 400
        elif advantage_status == AdvantageStatus.DISADVANTAGE:
            hit_chance = ((21 - (target.armor_class - attack.hit_bonus)) ** 2) / 400
        else:
            hit_chance = (21 - (target.armor_class - attack.hit_bonus)) / 20
        
        return max(0.05, min(0.95, hit_chance))  # Critical hit and miss probabilities

    def choose_action(self, combat_manager: 'CombatManager') -> Tuple[Action, Optional[str]]:
        available_actions = self.get_available_actions(combat_manager)
        
        if self.strategy == DecisionStrategy.RANDOM:
            chosen_action = random.choice(available_actions)
        elif self.strategy == DecisionStrategy.AGGRESSIVE:
            chosen_action = max(available_actions, key=lambda a: a.outcome.expected_damage)
        elif self.strategy == DecisionStrategy.DEFENSIVE:
            # Prioritize actions that don't provoke attacks or increase defenses
            defensive_actions = [a for a in available_actions if not isinstance(a.action, Attack) or a.action.name in ["Dodge", "Disengage"]]
            chosen_action = random.choice(defensive_actions) if defensive_actions else random.choice(available_actions)
        elif self.strategy == DecisionStrategy.SUPPORTIVE:
            # Prioritize healing or buff actions if available, otherwise choose randomly
            support_actions = [a for a in available_actions if a.outcome.expected_healing > 0 or any(effect in [StatusEffect.HELPING] for effect in a.outcome.status_effects)]
            chosen_action = random.choice(support_actions) if support_actions else random.choice(available_actions)
        
        return chosen_action.action, chosen_action.target
    


class ActionLog(BaseModel):
    round: int
    turn: int
    attacker: str
    target: str
    action_name: str
    attack_roll: int
    advantage_status: AdvantageStatus
    is_hit: bool
    damage_dealt: float
    attacker_threatened: bool
    target_ac: int
    attacker_hp_before: int
    attacker_hp_after: int
    target_hp_before: int
    target_hp_after: int

class CombatLog(BaseModel):
    actions: List[ActionLog] = field(default_factory=list)

class CombatManager(BaseModel):
    battle_map: BattleMap
    creatures: Dict[str, StatsBlock] = Field(default_factory=dict)
    actors: Dict[str, Actor] = Field(default_factory=dict)
    initiative_order: List[str] = Field(default_factory=list)
    current_turn_index: int = 0
    round: int = 1
    combat_log: CombatLog = Field(default_factory=CombatLog)

    def add_creature(self, creature: StatsBlock, position: Tuple[int, int], strategy: DecisionStrategy = DecisionStrategy.RANDOM):
        self.creatures[creature.id] = creature
        self.actors[creature.id] = Actor(stats_block=creature, strategy=strategy)
        self.battle_map.place_creature(creature.id, position)

    def roll_initiative(self):
        initiative_rolls = [(creature.id, creature.initiative + random.randint(1, 20)) 
                            for creature in self.creatures.values()]
        self.initiative_order = [id for id, _ in sorted(initiative_rolls, key=lambda x: x[1], reverse=True)]

    def start_combat(self):
        self.roll_initiative()
        self.current_turn_index = 0
        self.round = 1

    def next_turn(self):
        self.current_turn_index = (self.current_turn_index + 1) % len(self.initiative_order)
        if self.current_turn_index == 0:
            self.round += 1
        current_creature = self.creatures[self.initiative_order[self.current_turn_index]]
        current_creature.action_economy.reset()

    def get_current_creature(self) -> StatsBlock:
        return self.creatures[self.initiative_order[self.current_turn_index]]

    def is_combat_over(self) -> bool:
        alive_creatures = [creature for creature in self.creatures.values() if creature.current_hit_points > 0]
        return len(alive_creatures) <= 1

    def perform_attack(self, attacker_id: str, target_id: str, attack_name: str):
        attacker = self.creatures[attacker_id]
        target = self.creatures[target_id]

        attacker_pos = self.battle_map.get_creature_position(attacker_id)
        target_pos = self.battle_map.get_creature_position(target_id)

        if not self.battle_map.has_line_of_sight(attacker_pos, target_pos):
            raise ValueError("No line of sight to target")

        attack = next((a for a in attacker.actions if isinstance(a, Attack) and a.name == attack_name), None)
        if attack is None:
            raise ValueError(f"Attack {attack_name} not found")

        distance = self.battle_map.get_distance(attacker_pos, target_pos)
        if distance > attack.range.normal:
            raise ValueError("Target is out of range")

        is_threatened = self.battle_map.is_threatened(attacker_id)
        is_ranged_attack = attack.attack_type in [AttackType.RANGED_WEAPON, AttackType.RANGED_SPELL]
        
        advantage_status = AdvantageStatus.DISADVANTAGE if (is_threatened and is_ranged_attack) else AdvantageStatus.NONE

        attack_roll = self.roll_d20(advantage_status)
        total_attack_roll = attack_roll + attack.hit_bonus

        attacker_hp_before = attacker.current_hit_points
        target_hp_before = target.current_hit_points

        is_hit = total_attack_roll >= target.armor_class
        damage_dealt = 0

        if is_hit:
            damage = sum(d.dice.expected_value() for d in attack.damage)
            target.take_damage(int(damage))
            damage_dealt = damage
            print(f"{attacker.name} hits {target.name} for {damage} damage!")
            print(f"{target.name} now has {target.current_hit_points}/{target.max_hit_points.total_value} HP.")
        else:
            print(f"{attacker.name} misses {target.name}!")

        self.combat_log.actions.append(ActionLog(
            round=self.round,
            turn=self.current_turn_index,
            attacker=attacker.name,
            target=target.name,
            action_name=attack_name,
            attack_roll=total_attack_roll,
            advantage_status=advantage_status,
            is_hit=is_hit,
            damage_dealt=damage_dealt,
            attacker_threatened=is_threatened,
            target_ac=target.armor_class,
            attacker_hp_before=attacker_hp_before,
            attacker_hp_after=attacker.current_hit_points,
            target_hp_before=target_hp_before,
            target_hp_after=target.current_hit_points
        ))

    def perform_turn(self, actor_id: str):
        actor = self.actors[actor_id]
        action, target_id = actor.choose_action(self)
        
        if isinstance(action, Attack) and target_id:
            self.perform_attack(actor_id, target_id, action.name)
        else:
            # Handle non-attack actions
            print(f"{actor.stats_block.name} performs {action.name}")
            # Implement effects of non-attack actions

    def roll_d20(self, advantage_status: AdvantageStatus) -> int:
        if advantage_status == AdvantageStatus.ADVANTAGE:
            return max(random.randint(1, 20), random.randint(1, 20))
        elif advantage_status == AdvantageStatus.DISADVANTAGE:
            return min(random.randint(1, 20), random.randint(1, 20))
        else:
            return random.randint(1, 20)

    def get_valid_targets(self, attacker_id: str, attack_name: str) -> List[str]:
        attacker = self.creatures[attacker_id]
        attacker_pos = self.battle_map.get_creature_position(attacker_id)
        attack = next((a for a in attacker.actions if isinstance(a, Attack) and a.name == attack_name), None)
        if attack is None:
            return []

        valid_targets = []
        for target_id, target_pos in self.battle_map.get_all_creatures().items():
            if target_id != attacker_id:
                distance = self.battle_map.get_distance(attacker_pos, target_pos)
                if distance <= attack.range.normal and self.battle_map.has_line_of_sight(attacker_pos, target_pos):
                    valid_targets.append(target_id)

        return valid_targets

def print_combat_status(combat_manager: CombatManager):
    print(f"\nRound {combat_manager.round}")
    for creature in combat_manager.creatures.values():
        position = combat_manager.battle_map.get_creature_position(creature.id)
        print(f"{creature.name} at {position}: HP {creature.current_hit_points}/{creature.max_hit_points.total_value}")

def run_combat(combat_manager: CombatManager):
    combat_manager.start_combat()

    while not combat_manager.is_combat_over():
        print_combat_status(combat_manager)

        current_actor_id = combat_manager.initiative_order[combat_manager.current_turn_index]
        current_actor = combat_manager.actors[current_actor_id]
        print(f"\n{current_actor.stats_block.name}'s turn")

        combat_manager.perform_turn(current_actor_id)
        combat_manager.next_turn()

    winner = next(creature for creature in combat_manager.creatures.values() if creature.current_hit_points > 0)
    print(f"\nCombat over! {winner.name} wins with {winner.current_hit_points}/{winner.max_hit_points.total_value} HP remaining!")

    return combat_manager.combat_log

def print_combat_summary(combat_log: CombatLog):
    print("\nCombat Summary:")
    for action in combat_log.actions:
        advantage_str = f" ({action.advantage_status.value})" if action.advantage_status != AdvantageStatus.NONE else ""
        hit_str = "Hit" if action.is_hit else "Miss"
        print(f"Round {action.round}, Turn {action.turn}: {action.attacker} attacks {action.target} with {action.action_name}")
        print(f"  Attack Roll: {action.attack_roll}{advantage_str} vs AC {action.target_ac} - {hit_str}")
        if action.is_hit:
            print(f"  Damage Dealt: {action.damage_dealt}")
        print(f"  {action.attacker} HP: {action.attacker_hp_before} -> {action.attacker_hp_after}")
        print(f"  {action.target} HP: {action.target_hp_before} -> {action.target_hp_after}")
        print(f"  Attacker Threatened: {'Yes' if action.attacker_threatened else 'No'}")
        print()

def main():
    battle_map = BattleMap(width=2, height=1)
    combat_manager = CombatManager(battle_map=battle_map)

    goblin = create_goblin()
    skeleton = create_skeleton()

    combat_manager.add_creature(goblin, (0, 0), strategy=DecisionStrategy.AGGRESSIVE)
    combat_manager.add_creature(skeleton, (1, 0), strategy=DecisionStrategy.RANDOM)

    combat_log = run_combat(combat_manager)
    print_combat_summary(combat_log)

if __name__ == "__main__":
    main()