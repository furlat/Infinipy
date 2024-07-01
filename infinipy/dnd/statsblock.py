from __future__ import annotations
from typing import List, Union, TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .statsblock import StatsBlock
from pydantic import BaseModel, Field, computed_field
from enum import Enum
from typing import List, Union
from infinipy.dnd.docstrings import *

class Size(str, Enum):
    TINY = "Tiny"
    SMALL = "Small"
    MEDIUM = "Medium"
    LARGE = "Large"
    HUGE = "Huge"
    GARGANTUAN = "Gargantuan"

class MonsterType(str, Enum):
    ABERRATION = "Aberration"
    BEAST = "Beast"
    CELESTIAL = "Celestial"
    CONSTRUCT = "Construct"
    DRAGON = "Dragon"
    ELEMENTAL = "Elemental"
    FEY = "Fey"
    FIEND = "Fiend"
    GIANT = "Giant"
    HUMANOID = "Humanoid"
    MONSTROSITY = "Monstrosity"
    OOZE = "Ooze"
    PLANT = "Plant"
    UNDEAD = "Undead"

class Alignment(str, Enum):
    LAWFUL_GOOD = "Lawful Good"
    LAWFUL_NEUTRAL = "Lawful Neutral"
    LAWFUL_EVIL = "Lawful Evil"
    NEUTRAL_GOOD = "Neutral Good"
    TRUE_NEUTRAL = "True Neutral"
    NEUTRAL_EVIL = "Neutral Evil"
    CHAOTIC_GOOD = "Chaotic Good"
    CHAOTIC_NEUTRAL = "Chaotic Neutral"
    CHAOTIC_EVIL = "Chaotic Evil"
    UNALIGNED = "Unaligned"

class Ability(str, Enum):
    STR = "Strength"
    DEX = "Dexterity"
    CON = "Constitution"
    INT = "Intelligence"
    WIS = "Wisdom"
    CHA = "Charisma"

class Skills(str, Enum):
    ACROBATICS = "Acrobatics"
    ANIMAL_HANDLING = "Animal Handling"
    ARCANA = "Arcana"
    ATHLETICS = "Athletics"
    DECEPTION = "Deception"
    HISTORY = "History"
    INSIGHT = "Insight"
    INTIMIDATION = "Intimidation"
    INVESTIGATION = "Investigation"
    MEDICINE = "Medicine"
    NATURE = "Nature"
    PERCEPTION = "Perception"
    PERFORMANCE = "Performance"
    PERSUASION = "Persuasion"
    RELIGION = "Religion"
    SLEIGHT_OF_HAND = "Sleight of Hand"
    STEALTH = "Stealth"
    SURVIVAL = "Survival"

class SensesType(str, Enum):
    BLINDSIGHT = "Blindsight"
    DARKVISION = "Darkvision"
    TREMORSENSE = "Tremorsense"
    TRUESIGHT = "Truesight"

class DamageType(str, Enum):
    ACID = "Acid"
    BLUDGEONING = "Bludgeoning"
    COLD = "Cold"
    FIRE = "Fire"
    FORCE = "Force"
    LIGHTNING = "Lightning"
    NECROTIC = "Necrotic"
    PIERCING = "Piercing"
    POISON = "Poison"
    PSYCHIC = "Psychic"
    RADIANT = "Radiant"
    SLASHING = "Slashing"
    THUNDER = "Thunder"

class Language(str, Enum):
    COMMON = "Common"
    DWARVISH = "Dwarvish"
    ELVISH = "Elvish"
    GIANT = "Giant"
    GNOMISH = "Gnomish"
    GOBLIN = "Goblin"
    HALFLING = "Halfling"
    ORC = "Orc"
    ABYSSAL = "Abyssal"
    CELESTIAL = "Celestial"
    DRACONIC = "Draconic"
    DEEP_SPEECH = "Deep Speech"
    INFERNAL = "Infernal"
    PRIMORDIAL = "Primordial"
    SYLVAN = "Sylvan"
    UNDERCOMMON = "Undercommon"

class ActionType(str, Enum):
    ACTION = "Action"
    BONUS_ACTION = "Bonus Action"
    REACTION = "Reaction"
    MOVEMENT = "Movement"
    LEGENDARY_ACTION = "Legendary Action"
    LAIR_ACTION = "Lair Action"

class UsageType(str, Enum):
    RECHARGE = "Recharge"
    AT_WILL = "At Will"
    CHARGES = "Charges"

class RechargeType(str, Enum):
    SHORT_REST = "Short Rest"
    LONG_REST = "Long Rest"
    ROUND = "Round"

class AdvantageStatus(str, Enum):
    NONE = "None"
    ADVANTAGE = "Advantage"
    DISADVANTAGE = "Disadvantage"

class StatusEffect(str, Enum):
    DISADVANTAGE_ON_ATTACK_ROLLS = "Disadvantage on Attack Rolls"
    ADVANTAGE_ON_DEX_SAVES = "Advantage on Dexterity Saving Throws"
    HIDDEN = "Hidden"
    DODGING = "Dodging"
    HELPING = "Helping"
    DASHING = "Dashing"


## base models


class Speed(BaseModel):
    walk: int 
    fly: int = Field(0, description=fly_docstring)
    swim: int = Field(0, description=swim_docstring)
    burrow: int = Field(0, description=burrow_docstring)
    climb: int = Field(0, description=climb_docstring)

class AbilityScore(BaseModel):
    ability: Ability
    score: int

    @computed_field
    def modifier(self) -> int:
        return (self.score - 10) // 2

class AbilityScores(BaseModel):
    strength: AbilityScore = Field(AbilityScore(ability=Ability.STR, score=10), description=strength_docstring)
    dexterity: AbilityScore = Field(AbilityScore(ability=Ability.DEX, score=10), description=dexterity_docstring)
    constitution: AbilityScore = Field(AbilityScore(ability=Ability.CON, score=10), description=constitution_docstring)
    intelligence: AbilityScore = Field(AbilityScore(ability=Ability.INT, score=10), description=intelligence_docstring)
    wisdom: AbilityScore = Field(AbilityScore(ability=Ability.WIS, score=10), description=wisdom_docstring)
    charisma: AbilityScore = Field(AbilityScore(ability=Ability.CHA, score=10), description=charisma_docstring)

    @computed_field
    def saving_throws(self) -> List['SavingThrow']:
        return [SavingThrow(ability=ability, bonus=getattr(self, ability.value.lower()).modifier)
                for ability in Ability]

    @computed_field
    def skill_bonuses(self) -> List['SkillBonus']:
        skill_ability_map = {
            Skills.ATHLETICS: Ability.STR,
            Skills.ACROBATICS: Ability.DEX,
            Skills.SLEIGHT_OF_HAND: Ability.DEX,
            Skills.STEALTH: Ability.DEX,
            Skills.ARCANA: Ability.INT,
            Skills.HISTORY: Ability.INT,
            Skills.INVESTIGATION: Ability.INT,
            Skills.NATURE: Ability.INT,
            Skills.RELIGION: Ability.INT,
            Skills.ANIMAL_HANDLING: Ability.WIS,
            Skills.INSIGHT: Ability.WIS,
            Skills.MEDICINE: Ability.WIS,
            Skills.PERCEPTION: Ability.WIS,
            Skills.SURVIVAL: Ability.WIS,
            Skills.DECEPTION: Ability.CHA,
            Skills.INTIMIDATION: Ability.CHA,
            Skills.PERFORMANCE: Ability.CHA,
            Skills.PERSUASION: Ability.CHA,
        }
        return [SkillBonus(skill=skill, bonus=getattr(self, skill_ability_map[skill].value.lower()).modifier)
                for skill in Skills]

class SavingThrow(BaseModel):
    ability: Ability
    bonus: int

class SkillBonus(BaseModel):
    skill: Skills
    bonus: int

class Sense(BaseModel):
    type: SensesType
    range: int

class ActionCost(BaseModel):
    type: ActionType
    cost: int

class LimitedRecharge(BaseModel):
    recharge_type: RechargeType
    recharge_rate: int

class LimitedUsage(BaseModel):
    usage_type: UsageType
    usage_number: int
    recharge: Union[LimitedRecharge, None]

class Duration(BaseModel):
    time: Union[int, str]
    unit: str  # e.g., "round", "minute", "hour"
    concentration: bool = False

    def __str__(self):
        duration_str = f"{self.time} {self.unit}"
        if self.concentration:
            duration_str = f"Concentration, up to {duration_str}"
        return duration_str

class RangeType(str, Enum):
    REACH = "Reach"
    RANGE = "Range"

class TargetType(str, Enum):
    SELF = "Self"
    ONE_TARGET = "One Target"
    MULTIPLE_TARGETS = "Multiple Targets"
    AREA = "Area"
    ALLY = "Ally"  # Added this line

class ShapeType(str, Enum):
    SPHERE = "Sphere"
    CUBE = "Cube"
    CONE = "Cone"
    LINE = "Line"
    CYLINDER = "Cylinder"

class TargetRequirementType(str, Enum):
    HOSTILE = "Hostile"
    ALLY = "Ally"
    ANY = "Any"

class Range(BaseModel):
    type: RangeType
    normal: int
    long: Optional[int] = None

    def __str__(self):
        if self.type == RangeType.REACH:
            return f"{self.normal} ft."
        elif self.type == RangeType.RANGE:
            return f"{self.normal}/{self.long} ft." if self.long else f"{self.normal} ft."

class Targeting(BaseModel):
    type: TargetType
    shape: Union[ShapeType, None] = None
    size: Union[int, None] = None  # size of the area of effect
    line_of_sight: bool = True
    number_of_targets: Union[int, None] = None
    requirement: TargetRequirementType = TargetRequirementType.ANY
    description: str = ""

    def target_docstring(self):
        target_str = self.type.value
        if self.type == TargetType.AREA and self.shape and self.size:
            target_str += f" ({self.shape.value}, {self.size} ft.)"
        if self.number_of_targets:
            target_str += f", up to {self.number_of_targets} targets"
        if self.line_of_sight:
            target_str += ", requiring line of sight"
        if self.requirement != TargetRequirementType.ANY:
            target_str += f", {self.requirement.value.lower()} targets only"
        return target_str

class Action(BaseModel):
    name: str
    description: str
    cost: List[ActionCost]
    limited_usage: Union[LimitedUsage, None]
    targeting: Targeting
    status_effects: List[StatusEffect] = Field(default_factory=list)
    duration: Union[Duration, None] = None
    stats_block: 'StatsBlock'

    def action_docstring(self):
        target_description = self.targeting.target_docstring()
        return f"{self.description} Target: {target_description}."

class AttackType(str, Enum):
    MELEE_WEAPON = "Melee Weapon"
    RANGED_WEAPON = "Ranged Weapon"
    MELEE_SPELL = "Melee Spell"
    RANGED_SPELL = "Ranged Spell"

class Dice(BaseModel):
    dice_count: int
    dice_value: int
    modifier: int
    advantage_status: AdvantageStatus = AdvantageStatus.NONE

    def expected_value(self):
        base_average = self.dice_count * (self.dice_value + 1) / 2 + self.modifier
        if self.advantage_status == AdvantageStatus.ADVANTAGE:
            advantage_average = (self.dice_value + 1) * (2 * self.dice_value + 1) / (3 * self.dice_value)
            return self.dice_count * advantage_average + self.modifier
        if self.advantage_status == AdvantageStatus.DISADVANTAGE:
            disadvantage_average = self.dice_value * (self.dice_value + 1) / (3 * self.dice_value)
            return self.dice_count * disadvantage_average + self.modifier
        return base_average

class Damage(BaseModel):
    dice: Dice
    type: DamageType

    def average_damage(self):
        return self.dice.expected_value()


## weapons
class ArmorType(str, Enum):
    LIGHT = "Light"
    MEDIUM = "Medium"
    HEAVY = "Heavy"

class Armor(BaseModel):
    name: str
    type: ArmorType
    base_ac: int
    dex_bonus: bool
    max_dex_bonus: Optional[int] = None
    strength_requirement: Optional[int] = None
    stealth_disadvantage: bool = False

class Shield(BaseModel):
    name: str
    ac_bonus: int

class WeaponProperty(str, Enum):
    FINESSE = "Finesse"
    VERSATILE = "Versatile"
    RANGED = "Ranged"
    THROWN = "Thrown"
    TWO_HANDED = "Two-Handed"
    LIGHT = "Light"
    HEAVY = "Heavy"

class Weapon(BaseModel):
    name: str
    damage: Damage
    attack_type: AttackType
    properties: List[WeaponProperty]
    range: Range

class Attack(Action):
    attack_type: AttackType
    ability: Ability
    range: Range
    damage: List[Damage]
    weapon: Optional[Weapon] = None
    additional_effects: Union[str, None] = None

    @computed_field
    def hit_bonus(self) -> int:
        ability_modifier = getattr(self.stats_block.ability_scores, self.ability.value.lower()).modifier
        return ability_modifier + self.stats_block.proficiency_bonus

    @computed_field
    def average_damage(self) -> float:
        ability_modifier = getattr(self.stats_block.ability_scores, self.ability.value.lower()).modifier
        return sum(d.dice.expected_value() + ability_modifier for d in self.damage)

    def action_docstring(self):
        attack_range = str(self.range)
        ability_modifier = getattr(self.stats_block.ability_scores, self.ability.value.lower()).modifier
        damage_strings = [
            f"{d.dice.dice_count}d{d.dice.dice_value} + {ability_modifier} {d.type.value} damage" 
            for d in self.damage
        ]
        damage_string = " plus ".join(damage_strings)
        return f"{self.attack_type.value} Attack: +{self.hit_bonus} to hit, {attack_range}, {self.targeting.target_docstring()}. Hit: {damage_string}. Average damage: {self.average_damage:.1f}."
    
class Disengage(Action):
    def __init__(self, stats_block: 'StatsBlock'):
        super().__init__(
            name="Disengage",
            description="Your movement doesn't provoke opportunity attacks for the rest of the turn.",
            cost=[ActionCost(type=ActionType.ACTION, cost=1)],
            limited_usage=None,
            targeting=Targeting(type=TargetType.SELF),
            status_effects=[],
            duration=Duration(time=1, unit="turn"),
            stats_block=stats_block
        )

class Dodge(Action):
    def __init__(self, stats_block: 'StatsBlock'):
        super().__init__(
            name="Dodge",
            description="Until the start of your next turn, any attack roll made against you has disadvantage if you can see the attacker, and you make Dexterity saving throws with advantage. You lose this benefit if you are incapacitated or if your speed drops to 0.",
            cost=[ActionCost(type=ActionType.ACTION, cost=1)],
            limited_usage=None,
            targeting=Targeting(type=TargetType.SELF),
            status_effects=[StatusEffect.DISADVANTAGE_ON_ATTACK_ROLLS, StatusEffect.ADVANTAGE_ON_DEX_SAVES],
            duration=Duration(time=1, unit="round"),
            stats_block=stats_block
        )

class Help(Action):
    def __init__(self, stats_block: 'StatsBlock'):
        super().__init__(
            name="Help",
            description="You lend your aid to another creature in the completion of a task, giving them advantage on their next ability check, or you aid a friendly creature in attacking a creature within 5 feet of you, giving advantage on the next attack roll.",
            cost=[ActionCost(type=ActionType.ACTION, cost=1)],
            limited_usage=None,
            targeting=Targeting(type=TargetType.ALLY, number_of_targets=1, requirement=TargetRequirementType.ALLY),
            status_effects=[StatusEffect.HELPING],
            duration=Duration(time=1, unit="round"),
            stats_block=stats_block
        )

class Hide(Action):
    def __init__(self, stats_block: 'StatsBlock'):
        super().__init__(
            name="Hide",
            description="You make a Dexterity (Stealth) check in an attempt to hide.",
            cost=[ActionCost(type=ActionType.ACTION, cost=1)],
            limited_usage=None,
            targeting=Targeting(type=TargetType.SELF),
            status_effects=[StatusEffect.HIDDEN],
            duration=Duration(time="until discovered or you take an action", unit=""),
            stats_block=stats_block
        )

class Dash(Action):
    def __init__(self, stats_block: 'StatsBlock'):
        super().__init__(
            name="Dash",
            description="You gain extra movement for the current turn. The increase equals your speed, after applying any modifiers.",
            cost=[ActionCost(type=ActionType.ACTION, cost=1)],
            limited_usage=None,
            targeting=Targeting(type=TargetType.SELF),
            status_effects=[StatusEffect.DASHING],
            duration=Duration(time=1, unit="turn"),
            stats_block=stats_block
        )

from pydantic import BaseModel, Field, computed_field
from typing import List, Optional, Union
from enum import Enum

# Assuming all the necessary enums and other classes are defined above

class StatsBlock(BaseModel):
    size: Size = Field(..., description=size_docstring)
    type: MonsterType = Field(..., description=type_docstring)
    alignment: Alignment = Field(..., description=alignment_docstring)
    ability_scores: AbilityScores = Field(AbilityScores(), description=ability_scores_docstring)
    speed: Speed = Field(Speed(walk=30, fly=0, swim=0, burrow=0, climb=0), description=speed_docstring)
    saving_throws: List[SavingThrow] = Field([], description=saving_throws_docstring)
    skills: List[SkillBonus] = Field([], description=skills_docstring)
    vulnerabilities: List[DamageType] = Field([], description=vulnerabilities_resistances_immunities_docstring)
    resistances: List[DamageType] = Field([], description=vulnerabilities_resistances_immunities_docstring)
    immunities: List[DamageType] = Field([], description=vulnerabilities_resistances_immunities_docstring)
    senses: List[Sense] = Field([], description=senses_docstring)
    languages: List[Language] = Field([], description=languages_docstring)
    telepathy: int = Field(0, description=telepathy_docstring)
    challenge: float = Field(..., description=challenge_docstring)
    experience_points: int = Field(..., description=experience_points_docstring)
    special_traits: List[str] = Field([], description=special_traits_docstring)
    actions: List[Action] = Field(default_factory=list, description=actions_docstring)
    reactions: List[Action] = Field(default_factory=list, description=reactions_docstring)
    legendary_actions: List[Action] = Field(default_factory=list, description=legendary_actions_docstring)
    lair_actions: List[Action] = Field(default_factory=list, description=legendary_lair_docstring)
    regional_effects: List[str] = Field(default_factory=list, description=legendary_lair_docstring)
    
    armor: Optional[Armor] = None
    shield: Optional[Shield] = None
    weapons: List[Weapon] = Field(default_factory=list)
    
    base_ac: int = Field(default=10)
    computed_hit_points: int = Field(default=0)
    computed_passive_perception: int = Field(default=0)

    def __init__(self, **data):
        super().__init__(**data)
        self.add_default_actions()
        self._recompute_fields()

    def add_default_actions(self):
        self.add_action(Dodge(stats_block=self))
        self.add_action(Disengage(stats_block=self))
        self.add_action(Dash(stats_block=self))
        self.add_action(Hide(stats_block=self))
        self.add_action(Help(stats_block=self))

    def _recompute_fields(self):
        self._compute_armor_class()
        self._compute_hit_points()
        self._compute_passive_perception()

    @computed_field
    def proficiency_bonus(self) -> int:
        return max(2, ((self.challenge - 1) // 4) + 2)

    @computed_field
    def armor_class(self) -> int:
        return self.base_ac

    def _compute_armor_class(self):
        base_ac = 10 + self.ability_scores.dexterity.modifier
        if self.armor:
            base_ac = self.armor.base_ac
            if self.armor.dex_bonus:
                dex_bonus = self.ability_scores.dexterity.modifier
                if self.armor.max_dex_bonus is not None:
                    dex_bonus = min(dex_bonus, self.armor.max_dex_bonus)
                base_ac += dex_bonus

        if self.shield:
            base_ac += self.shield.ac_bonus

        self.base_ac = base_ac

    @computed_field
    def initiative(self) -> int:
        return self.ability_scores.dexterity.modifier

    @computed_field
    def hit_points(self) -> int:
        return self.computed_hit_points

    def _compute_hit_points(self):
        self.computed_hit_points = max(1, (8 + self.ability_scores.constitution.modifier) * int(self.challenge))

    @computed_field
    def passive_perception(self) -> int:
        return self.computed_passive_perception

    def _compute_passive_perception(self):
        perception_bonus = next((skill.bonus for skill in self.skills if skill.skill == Skills.PERCEPTION), 0)
        self.computed_passive_perception = 10 + self.ability_scores.wisdom.modifier + perception_bonus

    def add_action(self, action: Action):
        action.stats_block = self
        self.actions.append(action)

    def add_reaction(self, reaction: Action):
        reaction.stats_block = self
        self.reactions.append(reaction)

    def add_legendary_action(self, legendary_action: Action):
        legendary_action.stats_block = self
        self.legendary_actions.append(legendary_action)

    def add_lair_action(self, lair_action: Action):
        lair_action.stats_block = self
        self.lair_actions.append(lair_action)

    def equip_armor(self, armor: Armor):
        self.armor = armor
        self._recompute_fields()

    def unequip_armor(self):
        self.armor = None
        self._recompute_fields()

    def equip_shield(self, shield: Shield):
        self.shield = shield
        self._recompute_fields()

    def unequip_shield(self):
        self.shield = None
        self._recompute_fields()

    def add_weapon(self, weapon: Weapon):
        self.weapons.append(weapon)
        self.add_weapon_attack(weapon)

    def remove_weapon(self, weapon: Weapon):
        self.weapons.remove(weapon)
        self.actions = [action for action in self.actions if not (isinstance(action, Attack) and action.weapon == weapon)]

    def add_weapon_attack(self, weapon: Weapon):
        ability = Ability.DEX if WeaponProperty.FINESSE in weapon.properties else Ability.STR
        if weapon.attack_type == AttackType.RANGED_WEAPON:
            ability = Ability.DEX

        attack = Attack(
            name=weapon.name,
            description=f"{weapon.attack_type.value} Attack with {weapon.name}",
            cost=[ActionCost(type=ActionType.ACTION, cost=1)],
            limited_usage=None,
            attack_type=weapon.attack_type,
            ability=ability,
            range=weapon.range,
            damage=[weapon.damage],
            targeting=Targeting(type=TargetType.ONE_TARGET),
            stats_block=self,
            weapon=weapon
        )
        self.add_action(attack)

    def update_ability_scores(self, new_ability_scores: AbilityScores):
        self.ability_scores = new_ability_scores
        self._recompute_fields()
        # Update all actions that depend on ability scores
        for action in self.actions + self.reactions + self.legendary_actions + self.lair_actions:
            if isinstance(action, Attack):
                action.hit_bonus = action.hit_bonus  # This will trigger recomputation
                action.average_damage = action.average_damage  # This will trigger recomputation

if __name__ == "__main__":
    test_monster = StatsBlock(
        size=Size.MEDIUM,
        type=MonsterType.BEAST,
        alignment=Alignment.UNALIGNED,
        challenge=2,
        experience_points=450,
        ability_scores=AbilityScores(
            strength=AbilityScore(ability=Ability.STR, score=14),
            dexterity=AbilityScore(ability=Ability.DEX, score=16),
            constitution=AbilityScore(ability=Ability.CON, score=13),
            intelligence=AbilityScore(ability=Ability.INT, score=8),
            wisdom=AbilityScore(ability=Ability.WIS, score=12),
            charisma=AbilityScore(ability=Ability.CHA, score=10)
        ),
        skills=[SkillBonus(skill=Skills.PERCEPTION, bonus=2)]
    )

    print(f"Strength modifier: {test_monster.ability_scores.strength.modifier}")
    print(f"Dexterity saving throw bonus: {next(st for st in test_monster.ability_scores.saving_throws if st.ability == Ability.DEX).bonus}")
    print(f"Proficiency Bonus: {test_monster.proficiency_bonus}")
    print(f"Armor Class: {test_monster.armor_class}")
    print(f"Initiative: {test_monster.initiative}")
    print(f"Hit Points: {test_monster.hit_points}")
    print(f"Passive Perception: {test_monster.passive_perception}")

    # Create a weapon
    bite_weapon = Weapon(
        name="Bite",
        damage=Damage(dice=Dice(dice_count=1, dice_value=6, modifier=0), type=DamageType.PIERCING),
        attack_type=AttackType.MELEE_WEAPON,
        properties=[],
        range=Range(type=RangeType.REACH, normal=5)
    )

    # Add the weapon to the monster
    test_monster.add_weapon(bite_weapon)

    # Get the bite attack
    bite_attack = next(action for action in test_monster.actions if action.name == "Bite")

    print(f"\nBite Attack:")
    print(f"Hit Bonus: +{bite_attack.hit_bonus}")
    print(f"Average Damage: {bite_attack.average_damage}")
    print(bite_attack.action_docstring())

    print("\nAll Actions:")
    for action in test_monster.actions:
        print(f"- {action.name}")

    # Test equipping armor and shield
    leather_armor = Armor(
        name="Leather Armor",
        type=ArmorType.LIGHT,
        base_ac=11,
        dex_bonus=True
    )
    test_monster.equip_armor(leather_armor)
    print(f"\nAC after equipping leather armor: {test_monster.armor_class}")

    shield = Shield(name="Shield", ac_bonus=2)
    test_monster.equip_shield(shield)
    print(f"AC after equipping shield: {test_monster.armor_class}")

    # Test unequipping
    test_monster.unequip_shield()
    print(f"AC after unequipping shield: {test_monster.armor_class}")

    test_monster.unequip_armor()
    print(f"AC after unequipping armor: {test_monster.armor_class}")