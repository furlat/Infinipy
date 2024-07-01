from infinipy.dnd.statsblock import *
from typing import List

class GoblinDisengage(Action):
    def __init__(self, stats_block: 'StatsBlock'):
        super().__init__(
            name="Nimble Escape",
            description="The goblin can take the Disengage or Hide action as a bonus action on each of its turns.",
            cost=[ActionCost(type=ActionType.BONUS_ACTION, cost=1)],
            limited_usage=None,
            targeting=Targeting(type=TargetType.SELF),
            stats_block=stats_block
        )

def create_goblin() -> StatsBlock:
    goblin = StatsBlock(
        size=Size.SMALL,
        type=MonsterType.HUMANOID,
        alignment=Alignment.NEUTRAL_EVIL,
        ability_scores=AbilityScores(
            strength=AbilityScore(ability=Ability.STR, score=8),
            dexterity=AbilityScore(ability=Ability.DEX, score=14),
            constitution=AbilityScore(ability=Ability.CON, score=10),
            intelligence=AbilityScore(ability=Ability.INT, score=10),
            wisdom=AbilityScore(ability=Ability.WIS, score=8),
            charisma=AbilityScore(ability=Ability.CHA, score=8)
        ),
        speed=Speed(walk=30),
        skills=[
            SkillBonus(skill=Skills.STEALTH, bonus=6)
        ],
        senses=[
            Sense(type=SensesType.DARKVISION, range=60)
        ],
        languages=[Language.COMMON, Language.GOBLIN],
        challenge=0.25,
        experience_points=50,
        equipment=["Scimitar", "Shortbow", "Leather Armor", "Shield"]
    )

    goblin.add_action(Attack(
        name="Scimitar",
        description="Melee Weapon Attack",
        cost=[ActionCost(type=ActionType.ACTION, cost=1)],
        limited_usage=None,
        attack_type=AttackType.MELEE_WEAPON,
        ability=Ability.DEX,
        range=Range(type=RangeType.REACH, distance=5),
        damage=[
            Damage(dice=Dice(dice_count=1, dice_value=6, modifier=0), type=DamageType.SLASHING)
        ],
        targeting=Targeting(type=TargetType.ONE_TARGET),
        stats_block=goblin
    ))

    goblin.add_action(Attack(
        name="Shortbow",
        description="Ranged Weapon Attack",
        cost=[ActionCost(type=ActionType.ACTION, cost=1)],
        limited_usage=None,
        attack_type=AttackType.RANGED_WEAPON,
        ability=Ability.DEX,
        range=Range(type=RangeType.RANGE, distance="80/320"),
        damage=[
            Damage(dice=Dice(dice_count=1, dice_value=6, modifier=0), type=DamageType.PIERCING)
        ],
        targeting=Targeting(type=TargetType.ONE_TARGET),
        stats_block=goblin
    ))

    goblin.add_action(GoblinDisengage(stats_block=goblin))

    return goblin

def print_goblin_details(goblin: StatsBlock):
    print("\nGoblin Details:\n")
    print(f"Size: {goblin.size}")
    print(f"Type: {goblin.type}")
    print(f"Alignment: {goblin.alignment}")
    print(f"Ability Scores:")
    for ability in goblin.ability_scores.__dict__.values():
        if isinstance(ability, AbilityScore):
            print(f"  {ability.ability}: {ability.score} (Modifier: {ability.modifier})")
    print(f"Speed: Walk {goblin.speed.walk} ft")
    print(f"Armor Class: {goblin.armor_class}")
    print(f"Hit Points: {goblin.hit_points}")
    print(f"Proficiency Bonus: +{goblin.proficiency_bonus}")
    print("Saving Throws:")
    for st in goblin.ability_scores.saving_throws:
        print(f"  {st.ability}: +{st.bonus}")
    print("Skills:")
    for skill in goblin.skills:
        print(f"  {skill.skill}: +{skill.bonus}")
    print("Senses:")
    for sense in goblin.senses:
        print(f"  {sense.type}: {sense.range} ft")
    print(f"Languages: {', '.join(goblin.languages)}")
    print(f"Challenge Rating: {goblin.challenge} ({goblin.experience_points} XP)")
    print("Actions:")
    for action in goblin.actions:
        print(f"  - {action.name}: {action.action_docstring()}")
    print(f"Equipment: {', '.join(goblin.equipment)}")

def main():
    goblin = create_goblin()
    print_goblin_details(goblin)

if __name__ == "__main__":
    main()