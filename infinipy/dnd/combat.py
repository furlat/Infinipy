from dataclasses import dataclass, field
from typing import List, Dict, Tuple
import random
from infinipy.dnd.statsblock import StatsBlock, ActionEconomy, Attack, Damage, Dice, DamageType, AttackType, AdvantageStatus
from infinipy.dnd.battlemap import BattleMap
from infinipy.dnd.monsters.goblin import create_goblin
from infinipy.dnd.monsters.skeleton import create_skeleton

@dataclass
class ActionLog:
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

@dataclass
class CombatLog:
    actions: List[ActionLog] = field(default_factory=list)

class CombatManager:
    def __init__(self, battle_map: BattleMap):
        self.battle_map = battle_map
        self.creatures: Dict[str, StatsBlock] = {}
        self.initiative_order: List[str] = []
        self.current_turn_index: int = 0
        self.round: int = 1
        self.combat_log = CombatLog()

    def add_creature(self, creature: StatsBlock, position: Tuple[int, int]):
        self.creatures[creature.id] = creature
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

        current_creature = combat_manager.get_current_creature()
        print(f"\n{current_creature.name}'s turn")

        attacks = [a for a in current_creature.actions if isinstance(a, Attack)]
        if attacks:
            chosen_attack = random.choice(attacks)
            valid_targets = combat_manager.get_valid_targets(current_creature.id, chosen_attack.name)
            
            if valid_targets:
                target_id = random.choice(valid_targets)
                target = combat_manager.creatures[target_id]
                print(f"{current_creature.name} attempts to use {chosen_attack.name} on {target.name}")
                
                try:
                    combat_manager.perform_attack(current_creature.id, target_id, chosen_attack.name)
                except ValueError as e:
                    print(f"Attack failed: {e}")
            else:
                print(f"{current_creature.name} has no valid targets for {chosen_attack.name}")
        else:
            print(f"{current_creature.name} has no attacks available")

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
    combat_manager = CombatManager(battle_map)

    goblin = create_goblin()
    skeleton = create_skeleton()

    combat_manager.add_creature(goblin, (0, 0))
    combat_manager.add_creature(skeleton, (1, 0))

    combat_log = run_combat(combat_manager)
    print_combat_summary(combat_log)

if __name__ == "__main__":
    main()