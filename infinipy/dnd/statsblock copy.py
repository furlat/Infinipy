from pydantic import BaseModel, Field
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
    modifier: int

class AbilityScores(BaseModel):
    strength: AbilityScore = Field(AbilityScore(ability=Ability.STR, score=10, modifier=0), description=strength_docstring)
    dexterity: AbilityScore = Field(AbilityScore(ability=Ability.DEX, score=10, modifier=0), description=dexterity_docstring)
    constitution: AbilityScore = Field(AbilityScore(ability=Ability.CON, score=10, modifier=0), description=constitution_docstring)
    intelligence: AbilityScore = Field(AbilityScore(ability=Ability.INT, score=10, modifier=0), description=intelligence_docstring)
    wisdom: AbilityScore = Field(AbilityScore(ability=Ability.WIS, score=10, modifier=0), description=wisdom_docstring)
    charisma: AbilityScore = Field(AbilityScore(ability=Ability.CHA, score=10, modifier=0), description=charisma_docstring)

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
    distance: Union[int, str]  # e.g., 5 for reach or "80/320" for range

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

class Attack(Action):
    attack_type: AttackType
    hit_bonus: int
    range: Range
    damage: List[Damage]
    additional_effects: Union[str, None] = None

    def average_damage(self):
        return sum(d.average_damage() for d in self.damage) / len(self.damage)
    
    def action_docstring(self):
        attack_range = f"{self.range.type.value} {self.range.distance} ft."
        damage_strings = [f"{d.average_damage()} ({d.dice.dice_count}d{d.dice.dice_value} + {d.dice.modifier}) {d.type.value} damage" for d in self.damage]
        damage_string = " plus ".join(damage_strings)
        return f"{self.attack_type.value} Attack: +{self.hit_bonus} to hit, {attack_range}, {self.targeting.target_docstring()}. Hit: {damage_string}. With a total average damage of {self.average_damage()}."


### action subclasses 

class Disengage(Action):
    def __init__(self):
        super().__init__(
            name="Disengage",
            description="Your movement doesn't provoke opportunity attacks for the rest of the turn.",
            cost=[ActionCost(type=ActionType.ACTION, cost=1)],
            limited_usage=None,
            targeting=Targeting(type=TargetType.SELF),
            status_effects=[],
            duration=Duration(time=1, unit="turn")
        )

class Dodge(Action):
    def __init__(self):
        super().__init__(
            name="Dodge",
            description="Until the start of your next turn, any attack roll made against you has disadvantage if you can see the attacker, and you make Dexterity saving throws with advantage. You lose this benefit if you are incapacitated or if your speed drops to 0.",
            cost=[ActionCost(type=ActionType.ACTION, cost=1)],
            limited_usage=None,
            targeting=Targeting(type=TargetType.SELF),
            status_effects=[StatusEffect.DISADVANTAGE_ON_ATTACK_ROLLS, StatusEffect.ADVANTAGE_ON_DEX_SAVES],
            duration=Duration(time=1, unit="round")
        )

class Help(Action):
    def __init__(self):
        super().__init__(
            name="Help",
            description="You lend your aid to another creature in the completion of a task, giving them advantage on their next ability check, or you aid a friendly creature in attacking a creature within 5 feet of you, giving advantage on the next attack roll.",
            cost=[ActionCost(type=ActionType.ACTION, cost=1)],
            limited_usage=None,
            targeting=Targeting(type=TargetType.ALLY, number_of_targets=1, requirement=TargetRequirementType.ALLY),
            status_effects=[StatusEffect.HELPING],
            duration=Duration(time=1, unit="round")
        )

class Hide(Action):
    stealth_bonus: int

    def __init__(self, stealth_bonus: int):
        super().__init__(
            name="Hide",
            description="You make a Dexterity (Stealth) check in an attempt to hide.",
            cost=[ActionCost(type=ActionType.ACTION, cost=1)],
            limited_usage=None,
            targeting=Targeting(type=TargetType.SELF),
            status_effects=[StatusEffect.HIDDEN],
            duration=Duration(time="until discovered or you take an action", unit="")
        )
        self.stealth_bonus = stealth_bonus
        
class Dash(Action):
    def __init__(self):
        super().__init__(
            name="Dash",
            description="You gain extra movement for the current turn. The increase equals your speed, after applying any modifiers.",
            cost=[ActionCost(type=ActionType.ACTION, cost=1)],
            limited_usage=None,
            targeting=Targeting(type=TargetType.SELF),
            status_effects=[StatusEffect.DASHING],
            duration=Duration(time=1, unit="turn")
        )


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
    actions: List[Action] = Field([], description=actions_docstring)
    reactions: List[Action] = Field([], description=reactions_docstring)
    grapple_rules: str = Field("", description=grapple_rules_docstring)
    equipment: List[str] = Field([], description=equipment_docstring)
    legendary: bool = Field(False, description=legendary_creatures_docstring)
    legendary_actions: List[Action] = Field([], description=legendary_actions_docstring)
    lair: bool = Field(False, description=legendary_lair_docstring)
    lair_actions: List[Action] = Field([], description=legendary_lair_docstring)
    regional_effects: List[str] = Field([], description=legendary_lair_docstring)
