# example_frightened.py

from infinipy.dnd.statsblock import StatsBlock
from infinipy.dnd.monsters.goblin import create_goblin
from infinipy.dnd.monsters.skeleton import create_skeleton
from infinipy.dnd.conditions import Frightened, Duration, DurationType
from infinipy.dnd.actions import Attack
from infinipy.dnd.core import Skills

def print_creature_details(creature: StatsBlock):
    print(f"{creature.name} Details:")
    print(f"HP: {creature.current_hit_points}/{creature.max_hit_points}")
    print(f"Active Conditions: {', '.join([cond for cond in creature.active_conditions.keys()])}")
    print(f"Line of Sight: {creature.line_of_sight}")

def test_frightened_condition():
    goblin = create_goblin()
    skeleton = create_skeleton()
    
    print("\n=== Testing Frightened Condition ===")
    
    print("\n1. Applying Frightened condition to Goblin")
    frightened_condition = Frightened(name="Frightened", duration=Duration(time=3, type=DurationType.ROUNDS), source_entity_id=skeleton.id)
    goblin.apply_condition(frightened_condition)
    goblin.refresh_line_of_sight({skeleton.id})
    
    print("\n2. Goblin attacks while Frightened (Skeleton in sight)")
    perform_attack(goblin, skeleton)
    
    print("\n3. Goblin performs Stealth check while Frightened (Skeleton in sight)")
    perform_skill_check(goblin, Skills.STEALTH, 15)
    
    print("\n4. Removing Skeleton from Goblin's line of sight")
    goblin.refresh_line_of_sight(set())
    
    print("\n5. Goblin attacks while Frightened (Skeleton not in sight)")
    perform_attack(goblin, skeleton)
    
    print("\n6. Goblin performs Perception check while Frightened (Skeleton not in sight)")
    perform_skill_check(goblin, Skills.PERCEPTION, 15)
    
    print("\n7. Advancing time to expire the Frightened condition")
    for _ in range(3):
        goblin.update_conditions()
    
    print("\n8. Goblin attacks after Frightened condition expires")
    perform_attack(goblin, skeleton)
    
    print("\n9. Goblin performs Intimidation check after Frightened condition expires")
    perform_skill_check(goblin, Skills.INTIMIDATION, 15)

def perform_attack(attacker, defender):
    attack_action = next(action for action in attacker.actions if isinstance(action, Attack))
    hit, details = attack_action.roll_to_hit(defender, verbose=True)
    print(f"  Advantage status: {details['advantage_status']}")
    print(f"  Attack roll: {details['roll']}, Total: {details['roll'] + details['total_hit_bonus']}, AC: {details['armor_class']}")
    print(f"  Result: {'Hit' if hit else 'Miss'}")

def perform_skill_check(creature, skill, dc):
    roll, total, _ = creature.perform_skill_check(skill, dc, return_roll=True)
    skill_obj = creature.skills.get_skill(skill)
    advantage_status = skill_obj.bonus.get_advantage_status(creature)
    print(f"  Advantage status: {advantage_status}")
    print(f"  Skill check roll: {roll}, Total: {total}, DC: {dc}")
    print(f"  Result: {'Success' if total >= dc else 'Failure'}")

if __name__ == "__main__":
    test_frightened_condition()