from infinipy.dnd.statsblock import *
from infinipy.dnd.monsters.goblin import create_goblin
from infinipy.dnd.monsters.skeleton import create_skeleton
from infinipy.dnd.conditions import Blinded, Duration, DurationType

def print_goblin_details(goblin):
    print(f"Goblin Details:\nName: {goblin.name}\nSpeed: {goblin.speed.walk.get_value()} ft\nArmor Class: {goblin.armor_class.compute_base_ac(goblin.ability_scores)}")
    print(f"Hit Points: {goblin.current_hit_points}/{goblin.max_hit_points}\nProficiency Bonus: +{goblin.proficiency_bonus}")

def print_skeleton_details(skeleton):
    print(f"Skeleton Details:\nName: {skeleton.name}\nSpeed: {skeleton.speed.walk.get_value()} ft\nArmor Class: {skeleton.armor_class.compute_base_ac(skeleton.ability_scores)}")
    print(f"Hit Points: {skeleton.current_hit_points}/{skeleton.max_hit_points}\nProficiency Bonus: +{skeleton.proficiency_bonus}")

def test_blinded_condition():
    goblin = create_goblin()
    skeleton = create_skeleton()
    
    print("\n--- Initial State ---")
    print_goblin_details(goblin)
    print("\nSkeleton:")
    print_skeleton_details(skeleton)
    
    print("\n--- Goblin attacks Skeleton (no conditions) ---")
    attack_action = next(action for action in goblin.actions if isinstance(action, Attack))
    hit, details = attack_action.roll_to_hit(skeleton, verbose=True)
    print(f"Advantage status: {details['advantage_status']}")
    print(f"Attack roll: {details['roll']}, Total modifiers: {details['self_bonus'] - details['opponent_bonus']}")
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
    print_goblin_details(goblin)
    
    print("\n--- Goblin attacks Skeleton (Blinded condition) ---")
    attack_action = next(action for action in goblin.actions if isinstance(action, Attack))
    hit, details = attack_action.roll_to_hit(skeleton, verbose=True)
    print(f"Advantage status: {details['advantage_status']}")
    print(f"Attack roll: {details['roll']}, Total modifiers: {details['self_bonus'] - details['opponent_bonus']}")
    print(details)
    if hit:
        damage = attack_action.roll_damage()
        skeleton.take_damage(damage)
        print(f"Goblin hits Skeleton for {damage} damage. Skeleton HP: {skeleton.current_hit_points}")
    else:
        print(f"Goblin misses the attack due to being blinded. Required AC: {details['armor_class']}, Roll: {details['roll']}")
    
    print("\n--- Advancing Rounds ---")
    goblin.update_conditions()
    
    print("\n--- State After Advancing Rounds ---")
    print_goblin_details(goblin)
    
    goblin.update_conditions()
    
    print("\n--- State After Another Round ---")
    print_goblin_details(goblin)

def main():
    test_blinded_condition()

if __name__ == "__main__":
    main()
