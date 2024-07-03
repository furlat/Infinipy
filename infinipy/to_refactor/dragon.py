from infinipy.dnd.statsblock import *
from typing import List

class DragonAttack(Attack):
    def __init__(self, weapon: Weapon, stats_block: 'StatsBlock'):
        super().__init__(
            name=weapon.name,
            description=f"Attack with {weapon.name}",
            cost=[ActionCost(type=ActionType.ACTION, cost=1)],
            limited_usage=None,
            attack_type=weapon.attack_type,
            ability=Ability.STR,
            range=weapon.range,
            damage=[weapon.damage],
            targeting=Targeting(type=TargetType.ONE_TARGET),
            stats_block=stats_block,
            weapon=weapon
        )

class FireBreath(Action):
    def __init__(self, stats_block: 'StatsBlock'):
        super().__init__(
            name="Fire Breath",
            description="The dragon exhales fire in a 60-foot cone. Each creature in that area must make a DC 21 Dexterity saving throw, taking 63 (18d6) fire damage on a failed save, or half as much damage on a successful one.",
            cost=[ActionCost(type=ActionType.ACTION, cost=1)],
            limited_usage=LimitedUsage(
                usage_type=UsageType.RECHARGE,
                usage_number=1,
                recharge=LimitedRecharge(recharge_type=RechargeType.ROUND, recharge_rate=5)
            ),
            targeting=Targeting(
                type=TargetType.AREA,
                shape=ShapeType.CONE,
                size=60,
            ),
            stats_block=stats_block
        )

def create_adult_red_dragon() -> StatsBlock:
    dragon = StatsBlock(
        size=Size.HUGE,
        type=MonsterType.DRAGON,
        alignment=Alignment.CHAOTIC_EVIL,
        ability_scores=AbilityScores(
            strength=AbilityScore(ability=Ability.STR, score=27),
            dexterity=AbilityScore(ability=Ability.DEX, score=10),
            constitution=AbilityScore(ability=Ability.CON, score=25),
            intelligence=AbilityScore(ability=Ability.INT, score=16),
            wisdom=AbilityScore(ability=Ability.WIS, score=13),
            charisma=AbilityScore(ability=Ability.CHA, score=21)
        ),
        speed=Speed(walk=40, fly=80),
        immunities=[DamageType.FIRE],
        senses=[
            Sense(type=SensesType.BLINDSIGHT, range=60),
            Sense(type=SensesType.DARKVISION, range=120)
        ],
        languages=[Language.COMMON, Language.DRACONIC],
        challenge=17,
        experience_points=18000,
        special_traits=[
            "Legendary Resistance (3/Day): If the dragon fails a saving throw, it can choose to succeed instead."
        ],
    )

    # Add natural weapons
    bite = Weapon(
        name="Bite",
        damage=Damage(dice=Dice(dice_count=2, dice_value=10, modifier=8), type=DamageType.PIERCING),
        attack_type=AttackType.MELEE_WEAPON,
        properties=[],
        range=Range(type=RangeType.REACH, normal=10)
    )
    dragon.add_weapon(bite)
    dragon.add_action(DragonAttack(weapon=bite, stats_block=dragon))

    claw = Weapon(
        name="Claw",
        damage=Damage(dice=Dice(dice_count=2, dice_value=6, modifier=8), type=DamageType.SLASHING),
        attack_type=AttackType.MELEE_WEAPON,
        properties=[],
        range=Range(type=RangeType.REACH, normal=5)
    )
    dragon.add_weapon(claw)
    dragon.add_action(DragonAttack(weapon=claw, stats_block=dragon))

    tail = Weapon(
        name="Tail",
        damage=Damage(dice=Dice(dice_count=2, dice_value=8, modifier=8), type=DamageType.BLUDGEONING),
        attack_type=AttackType.MELEE_WEAPON,
        properties=[],
        range=Range(type=RangeType.REACH, normal=15)
    )
    dragon.add_weapon(tail)
    dragon.add_action(DragonAttack(weapon=tail, stats_block=dragon))

    dragon.add_action(FireBreath(stats_block=dragon))

    # Add legendary actions
    dragon.legendary_actions = [
        Action(
            name="Detect",
            description="The dragon makes a Wisdom (Perception) check.",
            cost=[ActionCost(type=ActionType.LEGENDARY_ACTION, cost=1)],
            limited_usage=None,
            targeting=Targeting(type=TargetType.SELF),
            stats_block=dragon
        ),
        DragonAttack(weapon=tail, stats_block=dragon),
        Action(
            name="Wing Attack (Costs 2 Actions)",
            description="The dragon beats its wings. Each creature within 10 ft. of the dragon must succeed on a DC 25 Dexterity saving throw or take 15 (2d6 + 8) bludgeoning damage and be knocked prone. The dragon can then fly up to half its flying speed.",
            cost=[ActionCost(type=ActionType.LEGENDARY_ACTION, cost=2)],
            limited_usage=None,
            targeting=Targeting(type=TargetType.AREA, shape=ShapeType.SPHERE, size=10),
            stats_block=dragon
        )
    ]

    # Add lair action
    dragon.lair_actions = [
        Action(
            name="Volcanic Gases",
            description="On initiative count 20 (losing initiative ties), the dragon can release a cloud of volcanic gases in a 20-foot-radius sphere centered on a point the dragon can see within 120 feet of it. The sphere spreads around corners, and its area is lightly obscured. It lasts until the initiative count 20 of the next round.",
            cost=[ActionCost(type=ActionType.LAIR_ACTION, cost=1)],
            limited_usage=None,
            targeting=Targeting(type=TargetType.AREA, shape=ShapeType.SPHERE, size=20),
            stats_block=dragon
        )
    ]

    dragon.regional_effects = [
        "The region containing a legendary red dragon's lair is warped by the dragon's magic, which creates one or more of the following effects:",
        "- Small earthquakes are common within 6 miles of the dragon's lair.",
        "- Water sources within 1 mile of the lair are supernaturally warm and tainted by sulfur.",
        "- Rocky fissures within 1 mile of the dragon's lair form portals to the Elemental Plane of Fire, allowing creatures of elemental fire into the world to dwell nearby."
    ]

    return dragon

def print_dragon_details(dragon: StatsBlock):
    print("\nAdult Red Dragon Details:\n")
    print(f"Size: {dragon.size.value}")
    print(f"Type: {dragon.type.value}")
    print(f"Alignment: {dragon.alignment.value}")
    print(f"Ability Scores:")
    for ability in Ability:
        score = getattr(dragon.ability_scores, ability.value.lower())
        print(f"  {ability.value}: {score.score} (Modifier: {score.modifier})")
    print(f"Speed: Walk {dragon.speed.walk} ft, Fly {dragon.speed.fly} ft")
    print(f"Armor Class: {dragon.armor_class}")
    print(f"Hit Points: {dragon.hit_points}")
    print(f"Proficiency Bonus: +{dragon.proficiency_bonus}")
    print("Saving Throws:")
    for st in dragon.ability_scores.saving_throws:
        print(f"  {st.ability.value}: +{st.bonus}")
    print("Skills:")
    for skill in dragon.ability_scores.skill_bonuses:
        print(f"  {skill.skill.value}: +{skill.bonus}")
    print("Damage Immunities: " + ", ".join([i.value for i in dragon.immunities]))
    print("Senses:")
    for sense in dragon.senses:
        print(f"  {sense.type.value}: {sense.range} ft")
    print(f"Languages: {', '.join([lang.value for lang in dragon.languages])}")
    print(f"Challenge Rating: {dragon.challenge} ({dragon.experience_points} XP)")
    print("Special Traits:")
    for trait in dragon.special_traits:
        print(f"  {trait}")
    print("Actions:")
    for action in dragon.actions:
        print(f"  - {action.name}: {action.action_docstring()}")
    print("Legendary Actions:")
    for action in dragon.legendary_actions:
        print(f"  - {action.name}: {action.description}")
    print("Lair Actions:")
    for action in dragon.lair_actions:
        print(f"  - {action.name}: {action.description}")
    print("Regional Effects:")
    for effect in dragon.regional_effects:
        print(f"  {effect}")

def main():
    dragon = create_adult_red_dragon()
    print_dragon_details(dragon)

if __name__ == "__main__":
    main()