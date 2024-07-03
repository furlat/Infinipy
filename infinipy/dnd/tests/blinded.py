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
    
    print("\n--- Initial State ---")
    print_creature_details(goblin)
    print("\n")
    print_creature_details(skeleton)
    
    print("\n--- Goblin attacks Skeleton (no conditions) ---")
    attack_action = next(action for action in goblin.actions if isinstance(action, Attack))
    hit, details = attack_action.roll_to_hit(skeleton, verbose=True)
    print(f"Advantage status: {details['advantage_status']}")
    print(f"Attack roll: {details['roll']}, Total hit bonus: {details['total_hit_bonus']}")
    print(details)
    if hit:
        damage = attack_action.roll_damage()
        skeleton.take_damage(damage)
        print(f"Goblin hits Skeleton for {damage} damage. Skeleton HP: {skeleton.current_hit_points}")
    else:
        print(f"Goblin misses the attack. Required AC: {details['armor_class']}, Roll: {details['roll']}")
    
    # Apply the Blinded condition to the goblin
    blinded_condition = Blinded(name="Blinded", duration=Duration(time=1, type=DurationType.ROUNDS))
    goblin.apply_condition(blinded_condition)
    
    print("\n--- State After Applying Blinded Condition ---")
    print_creature_details(goblin)
    
    print("\n--- Goblin attacks Skeleton (Blinded condition) ---")
    attack_action = next(action for action in goblin.actions if isinstance(action, Attack))
    hit, details = attack_action.roll_to_hit(skeleton, verbose=True)
    print(f"Advantage status: {details['advantage_status']}")
    print(f"Attack roll: {details['roll']}, Total hit bonus: {details['total_hit_bonus']}")
    print(details)
    if hit:
        damage = attack_action.roll_damage()
        skeleton.take_damage(damage)
        print(f"Goblin hits Skeleton for {damage} damage. Skeleton HP: {skeleton.current_hit_points}")
    else:
        print(f"Goblin misses the attack due to being blinded. Required AC: {details['armor_class']}, Roll: {details['roll']}")
    
    print("\n--- Skeleton attacks Blinded Goblin ---")
    skeleton_attack = next(action for action in skeleton.actions if isinstance(action, Attack))
    hit, details = skeleton_attack.roll_to_hit(goblin, verbose=True)
    print(f"Advantage status: {details['advantage_status']}")
    print(f"Attack roll: {details['roll']}, Total hit bonus: {details['total_hit_bonus']}")
    print(details)
    if hit:
        damage = skeleton_attack.roll_damage()
        goblin.take_damage(damage)
        print(f"Skeleton hits Goblin for {damage} damage. Goblin HP: {goblin.current_hit_points}")
    else:
        print(f"Skeleton misses the attack. Required AC: {details['armor_class']}, Roll: {details['roll']}")
    
    print("\n--- Advancing Rounds ---")
    goblin.update_conditions()
    
    print("\n--- State After Advancing Rounds ---")
    print_creature_details(goblin)
    
    goblin.update_conditions()
    
    print("\n--- State After Another Round ---")
    print_creature_details(goblin)
    
    print("\n--- Goblin attacks Skeleton (after Blinded condition expires) ---")
    attack_action = next(action for action in goblin.actions if isinstance(action, Attack))
    hit, details = attack_action.roll_to_hit(skeleton, verbose=True)
    print(f"Advantage status: {details['advantage_status']}")
    print(f"Attack roll: {details['roll']}, Total hit bonus: {details['total_hit_bonus']}")
    print(details)
    if hit:
        damage = attack_action.roll_damage()
        skeleton.take_damage(damage)
        print(f"Goblin hits Skeleton for {damage} damage. Skeleton HP: {skeleton.current_hit_points}")
    else:
        print(f"Goblin misses the attack. Required AC: {details['armor_class']}, Roll: {details['roll']}")

def main():
    test_blinded_condition()

if __name__ == "__main__":
    main()