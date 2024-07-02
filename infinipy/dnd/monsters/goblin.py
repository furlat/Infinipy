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
        name = "Goblin",
        size=Size.SMALL,
        type=MonsterType.HUMANOID,
        alignment=Alignment.NEUTRAL_EVIL,
        ability_scores=AbilityScores(
            strength=AbilityScore(ability=Ability.STR, score=ModifiableValue(base_value=8)),
            dexterity=AbilityScore(ability=Ability.DEX, score=ModifiableValue(base_value=14)),
            constitution=AbilityScore(ability=Ability.CON, score=ModifiableValue(base_value=10)),
            intelligence=AbilityScore(ability=Ability.INT, score=ModifiableValue(base_value=10)),
            wisdom=AbilityScore(ability=Ability.WIS, score=ModifiableValue(base_value=8)),
            charisma=AbilityScore(ability=Ability.CHA, score=ModifiableValue(base_value=8))
        ),
        speed=Speed(walk=ModifiableValue(base_value=30)),
        skills=[SkillBonus(skill=Skills.STEALTH, bonus=6)],
        senses=[Sense(type=SensesType.DARKVISION, range=60)],
        languages=[Language.COMMON, Language.GOBLIN],
        challenge=0.25,
        experience_points=50,
        special_traits=["Nimble Escape: The goblin can take the Disengage or Hide action as a bonus action on each of its turns."],
        # Initialize the new required fields
        max_hit_points=ModifiableValue(base_value=7),  # 2d6 average
        current_hit_points=7,
        action_economy=ActionEconomy(speed=30)
    )

    leather_armor = Armor(name="Leather Armor", type=ArmorType.LIGHT, base_ac=11, dex_bonus=True)
    goblin.equip_armor(leather_armor)
    shield = Shield(name="Shield", ac_bonus=2)
    goblin.equip_shield(shield)

    scimitar = Weapon(
        name="Scimitar",
        damage=Damage(dice=Dice(dice_count=1, dice_value=6, modifier=0), type=DamageType.SLASHING),
        attack_type=AttackType.MELEE_WEAPON,
        properties=[WeaponProperty.FINESSE],
        range=Range(type=RangeType.REACH, normal=5)
    )
    goblin.add_weapon(scimitar)

    shortbow = Weapon(
        name="Shortbow",
        damage=Damage(dice=Dice(dice_count=1, dice_value=6, modifier=0), type=DamageType.PIERCING),
        attack_type=AttackType.RANGED_WEAPON,
        properties=[WeaponProperty.RANGED],
        range=Range(type=RangeType.RANGE, normal=80, long=320)
    )
    goblin.add_weapon(shortbow)

    goblin.add_action(GoblinDisengage(stats_block=goblin))

    return goblin

def print_goblin_details(goblin: StatsBlock):
    print("\nGoblin Details:\n")
    print(f"Size: {goblin.size.value}")
    print(f"Type: {goblin.type.value}")
    print(f"Alignment: {goblin.alignment.value}")
    print(f"Ability Scores:")
    for ability in [Ability.STR, Ability.DEX, Ability.CON, Ability.INT, Ability.WIS, Ability.CHA]:
        score = getattr(goblin.ability_scores, ability.value.lower())
        print(f"  {ability.value}: {score.score.total_value} (Modifier: {score.modifier})")
    print(f"Speed: Walk {goblin.speed.walk.total_value} ft")
    print(f"Armor Class: {goblin.armor_class}")
    print(f"Hit Points: {goblin.hit_points}")
    print(f"Proficiency Bonus: +{goblin.proficiency_bonus}")
    print("Saving Throws:")
    for st in goblin.ability_scores.saving_throws:
        print(f"  {st.ability.value}: +{st.bonus}")
    print("Skills:")
    for skill in goblin.ability_scores.skill_bonuses:
        print(f"  {skill.skill.value}: +{skill.bonus}")
    print("Senses:")
    for sense in goblin.senses:
        print(f"  {sense.type.value}: {sense.range} ft")
    print(f"Languages: {', '.join([lang.value for lang in goblin.languages])}")
    print(f"Challenge Rating: {goblin.challenge} ({goblin.experience_points} XP)")
    print("Special Traits:")
    for trait in goblin.special_traits:
        print(f"  - {trait}")
    print("Actions:")
    for action in goblin.actions:
        print(f"  - {action.name}: {action.action_docstring()}")
    print("Reactions:")
    for reaction in goblin.reactions:
        print(f"  - {reaction.name}: {reaction.description}")
    print(f"Equipment: {', '.join([weapon.name for weapon in goblin.weapons])}, "
          f"{goblin.armor.name if goblin.armor else 'No Armor'}, "
          f"{goblin.shield.name if goblin.shield else 'No Shield'}")

def main():
    goblin = create_goblin()
    print_goblin_details(goblin)

    # Demonstrate modifiers
    print("\nDemonstrating Modifiers:")
    goblin.ability_scores.dexterity.score.add_modifier(2, "Potion of Cat's Grace", 10)
    print(f"Dexterity after Cat's Grace potion: {goblin.ability_scores.dexterity.score.total_value}")
    
    goblin.speed.walk.add_modifier(10, "Boots of Speed", -1)
    print(f"Walking speed with Boots of Speed: {goblin.speed.walk.total_value}")

    goblin.base_ac.add_modifier(1, "Ring of Protection", -1)
    print(f"AC with Ring of Protection: {goblin.armor_class}")

if __name__ == "__main__":
    main()