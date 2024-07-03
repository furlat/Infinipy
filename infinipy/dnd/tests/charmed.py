from infinipy.dnd.statsblock import StatsBlock
from infinipy.dnd.monsters.goblin import create_goblin
from infinipy.dnd.monsters.skeleton import create_skeleton
from infinipy.dnd.conditions import Charmed, Duration, DurationType
from infinipy.dnd.actions import Attack

def print_creature_details(creature: StatsBlock):
    print(f"{creature.name} Details:")
    print(f"Speed: {creature.speed.walk.get_value(creature)} ft")
    print(f"Armor Class: {creature.armor_class.get_value(creature)}")
    print(f"Hit Points: {creature.current_hit_points}/{creature.max_hit_points}")
    print(f"Proficiency Bonus: +{creature.proficiency_bonus}")
    print(f"Active Conditions: {', '.join([cond for cond in creature.active_conditions.keys()])}")

def test_charmed_condition():
    goblin = create_goblin()
    skeleton = create_skeleton()
    
    print("\n--- Initial State ---")
    print_creature_details(goblin)
    print("\n")
    print_creature_details(skeleton)
    
    print("\n--- Skeleton attacks Goblin (no conditions) ---")
    attack_action = next(action for action in skeleton.actions if isinstance(action, Attack))
    context = {"source": skeleton, "target": goblin}
    can_attack, reason = attack_action.prerequisite(context)
    if can_attack:
        hit, details = attack_action.roll_to_hit(goblin, verbose=True)
        print(f"Attack roll: {details['roll']}, Total hit bonus: {details['total_hit_bonus']}")
        if hit:
            damage = attack_action.roll_damage()
            goblin.take_damage(damage)
            print(f"Skeleton hits Goblin for {damage} damage. Goblin HP: {goblin.current_hit_points}")
        else:
            print(f"Skeleton misses the attack. Required AC: {details['armor_class']}, Roll: {details['roll']}")
    else:
        print(f"Skeleton cannot attack Goblin: {reason}")
    
    # Apply the Charmed condition to the skeleton
    charmed_condition = Charmed(name="Charmed", duration=Duration(time=1, type=DurationType.ROUNDS), source_entity_id=goblin.id)
    skeleton.apply_condition(charmed_condition)
    
    print("\n--- State After Applying Charmed Condition ---")
    print_creature_details(skeleton)
    
    print("\n--- Skeleton tries to attack Goblin (Charmed condition) ---")
    can_attack, reason = attack_action.prerequisite(context)
    if can_attack:
        hit, details = attack_action.roll_to_hit(goblin, verbose=True)
        print(f"Attack roll: {details['roll']}, Total hit bonus: {details['total_hit_bonus']}")
        if hit:
            damage = attack_action.roll_damage()
            goblin.take_damage(damage)
            print(f"Skeleton hits Goblin for {damage} damage. Goblin HP: {goblin.current_hit_points}")
        else:
            print(f"Skeleton misses the attack. Required AC: {details['armor_class']}, Roll: {details['roll']}")
    else:
        print(f"Skeleton cannot attack Goblin: {reason}")
    
    print("\n--- Advancing Time ---")
    skeleton.update_conditions()
    
    print("\n--- State After Advancing Time  this should be the last blinded turn---")
    print_creature_details(skeleton)
    
    print("\n--- Advancing Time ---")
    skeleton.update_conditions()
    print_creature_details(skeleton)
    print("\n--- Skeleton tries to attack Goblin (after Charmed condition expires) ---")
    can_attack, reason = attack_action.prerequisite(context)
    if can_attack:
        hit, details = attack_action.roll_to_hit(goblin, verbose=True)
        print(f"Attack roll: {details['roll']}, Total hit bonus: {details['total_hit_bonus']}")
        if hit:
            damage = attack_action.roll_damage()
            goblin.take_damage(damage)
            print(f"Skeleton hits Goblin for {damage} damage. Goblin HP: {goblin.current_hit_points}")
        else:
            print(f"Skeleton misses the attack. Required AC: {details['armor_class']}, Roll: {details['roll']}")
    else:
        print(f"Skeleton cannot attack Goblin: {reason}")

def main():
    test_charmed_condition()

if __name__ == "__main__":
    main()