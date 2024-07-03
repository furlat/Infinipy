from infinipy.dnd.statsblock import StatsBlock, Attack
from infinipy.dnd.battlemap import BattleMap, create_creature_copy
from infinipy.dnd.combat import CombatManager
from infinipy.dnd.monsters.goblin import create_goblin
from infinipy.dnd.monsters.skeleton import create_skeleton  # Assuming you've created this file
import random

def setup_combat():
    battle_map = BattleMap(width=2, height=1)
    combat_manager = CombatManager(battle_map)

    goblin = create_goblin()
    skeleton = create_skeleton()

    combat_manager.add_creature(goblin, (0, 0))
    combat_manager.add_creature(skeleton, (1, 0))

    return combat_manager

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

        # Simple AI: choose a random attack and a random target
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

def main():
    combat_manager = setup_combat()
    run_combat(combat_manager)

if __name__ == "__main__":
    main()