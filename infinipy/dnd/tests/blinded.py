from infinipy.dnd.statsblock import *
from infinipy.dnd.monsters.goblin import create_goblin
from infinipy.dnd.monsters.skeleton import create_skeleton
from infinipy.dnd.conditions import Blinded, Duration, DurationType

def print_creature_details(creature):
    print(f"{creature.name} Details:")
    print(f"Speed: {creature.speed.walk.get_value(creature)} ft")
    print(f"Armor Class: {creature.armor_class.get_value(creature)}")
    print(f"Hit Points: {creature.current_hit_points}/{creature.max_hit_points}")
    print(f"Proficiency Bonus: +{creature.proficiency_bonus}")
    print(f"Active Conditions: {', '.join([cond[0] for cond in creature.active_conditions.keys()])}")

def test_blinded_condition():
    goblin = create_goblin()
    skeleton = create_skeleton()
    
    print("\n=== Testing Blinded Condition ===")
    
    print("\n1. Initial State")
    print_creature_details(goblin)
    
    print("\n2. Applying Blinded condition to Goblin")
    blinded_condition = Blinded(name="Blinded", duration=Duration(time=3, type=DurationType.ROUNDS))
    goblin.apply_condition(blinded_condition)
    print_creature_details(goblin)
    
    print("\n3. Goblin attempts a normal Perception check")
    goblin.perform_skill_check(Skills.PERCEPTION, 15, context={'requires_sight': False})
    
    print("\n4. Goblin attempts a sight-based Perception check")
    goblin.perform_skill_check(Skills.PERCEPTION, 15, context={'requires_sight': True})
    
    print("\n5. Goblin attacks Skeleton")
    perform_attack(goblin, skeleton)
    
    print("\n6. Skeleton attacks Blinded Goblin")
    perform_attack(skeleton, goblin)
    
    print("\n7. Advancing time to expire the Blinded condition")
    for _ in range(3):
        goblin.update_conditions()
    print_creature_details(goblin)
    
    print("\n8. Goblin attacks Skeleton after Blinded condition expires")
    perform_attack(goblin, skeleton)

def perform_attack(attacker, defender):
    attack_action = next(action for action in attacker.actions if isinstance(action, Attack))
    hit, details = attack_action.roll_to_hit(defender, verbose=True)
    print(f"  Advantage status: {details['advantage_status']}")
    print(f"  Attack roll: {details['roll']}, Total: {details['roll'] + details['total_hit_bonus']}, AC: {details['armor_class']}")
    print(f"  Result: {'Hit' if hit else 'Miss'}")

if __name__ == "__main__":
    test_blinded_condition()