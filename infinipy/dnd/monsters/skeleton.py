from infinipy.dnd.statsblock import *
from typing import List

class SkeletonAttack(Attack):
    def __init__(self, name: str, description: str, ability: Ability, damage: List[Damage], attack_type: AttackType, stats_block: 'StatsBlock'):
        super().__init__(
            name=name,
            description=description,
            cost=[ActionCost(type=ActionType.ACTION, cost=1)],
            limited_usage=None,
            attack_type=attack_type,
            ability=ability,
            range=Range(type=RangeType.REACH, distance=5),
            damage=damage,
            targeting=Targeting(type=TargetType.ONE_TARGET),
            stats_block=stats_block
        )

def create_skeleton() -> StatsBlock:
    skeleton = StatsBlock(
        size=Size.MEDIUM,
        type=MonsterType.UNDEAD,
        alignment=Alignment.LAWFUL_EVIL,
        ability_scores=AbilityScores(
            strength=AbilityScore(ability=Ability.STR, score=10),
            dexterity=AbilityScore(ability=Ability.DEX, score=14),
            constitution=AbilityScore(ability=Ability.CON, score=15),
            intelligence=AbilityScore(ability=Ability.INT, score=6),
            wisdom=AbilityScore(ability=Ability.WIS, score=8),
            charisma=AbilityScore(ability=Ability.CHA, score=5)
        ),
        speed=Speed(walk=30),
        resistances=[DamageType.POISON],
        immunities=[DamageType.POISON],
        senses=[Sense(type=SensesType.DARKVISION, range=60)],
        languages=[Language.COMMON],
        challenge=0.25,
        experience_points=50,
        special_traits=[
            "Undead Fortitude: If damage reduces the skeleton to 0 hit points, it must make a Constitution saving throw with a DC of 5 + the damage taken, unless the damage is radiant or from a critical hit. On a success, the skeleton drops to 1 hit point instead."
        ],
        equipment=["Shortsword", "Shortbow", "Leather Armor"]
    )

    skeleton.add_action(SkeletonAttack(
        name="Shortsword",
        description="A shortsword slash.",
        ability=Ability.DEX,
        damage=[Damage(dice=Dice(dice_count=1, dice_value=6, modifier=0), type=DamageType.PIERCING)],
        attack_type=AttackType.MELEE_WEAPON,
        stats_block=skeleton
    ))

    skeleton.add_action(SkeletonAttack(
        name="Shortbow",
        description="A shortbow shot.",
        ability=Ability.DEX,
        damage=[Damage(dice=Dice(dice_count=1, dice_value=6, modifier=0), type=DamageType.PIERCING)],
        attack_type=AttackType.RANGED_WEAPON,
        stats_block=skeleton
    ))

    return skeleton

def print_skeleton_details(skeleton: StatsBlock):
    print("\nSkeleton Details:\n")
    print(f"Size: {skeleton.size}")
    print(f"Type: {skeleton.type}")
    print(f"Alignment: {skeleton.alignment}")
    print(f"Ability Scores:")
    for ability in skeleton.ability_scores.__dict__.values():
        if isinstance(ability, AbilityScore):
            print(f"  {ability.ability}: {ability.score} (Modifier: {ability.modifier})")
    print(f"Speed: Walk {skeleton.speed.walk} ft")
    print(f"Armor Class: {skeleton.armor_class}")
    print(f"Hit Points: {skeleton.hit_points}")
    print(f"Proficiency Bonus: +{skeleton.proficiency_bonus}")
    print("Saving Throws:")
    for st in skeleton.ability_scores.saving_throws:
        print(f"  {st.ability}: +{st.bonus}")
    print("Skills:")
    for skill in skeleton.skills:
        print(f"  {skill.skill}: +{skill.bonus}")
    print("Damage Resistances: " + ", ".join([str(r) for r in skeleton.resistances]))
    print("Damage Immunities: " + ", ".join([str(i) for i in skeleton.immunities]))
    print("Senses:")
    for sense in skeleton.senses:
        print(f"  {sense.type}: {sense.range} ft")
    print(f"Languages: {', '.join(skeleton.languages)}")
    print(f"Challenge Rating: {skeleton.challenge} ({skeleton.experience_points} XP)")
    print("Special Traits:")
    for trait in skeleton.special_traits:
        print(f"  {trait}")
    print("Actions:")
    for action in skeleton.actions:
        print(f"  - {action.name}: {action.action_docstring()}")
    print(f"Equipment: {', '.join(skeleton.equipment)}")

def main():
    skeleton = create_skeleton()
    print_skeleton_details(skeleton)

if __name__ == "__main__":
    main()