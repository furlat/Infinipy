from __future__ import annotations
from typing import List, Union, TYPE_CHECKING, Optional, Dict, Tuple, Set, Callable, Any

if TYPE_CHECKING:
    from .statsblock import StatsBlock
from pydantic import BaseModel, Field, computed_field
from enum import Enum
from typing import List, Union
from infinipy.dnd.docstrings import *
import uuid
import random
from infinipy.dnd.contextual import ModifiableValue, AdvantageStatus, AdvantageTracker, ContextualEffects

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



class StatusEffect(str, Enum):
    DISADVANTAGE_ON_ATTACK_ROLLS = "Disadvantage on Attack Rolls"
    ADVANTAGE_ON_DEX_SAVES = "Advantage on Dexterity Saving Throws"
    HIDDEN = "Hidden"
    DODGING = "Dodging"
    HELPING = "Helping"
    DASHING = "Dashing"

class DurationType(str, Enum):
    INSTANTANEOUS = "instantaneous"
    ROUNDS = "rounds"
    MINUTES = "minutes"
    HOURS = "hours"
    INDEFINITE = "indefinite"

HEARING_DEPENDENT_ABILITIES = {Skills.PERCEPTION, Skills.PERFORMANCE, Skills.INSIGHT}

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

class Dice(BaseModel):
    dice_count: int
    dice_value: int
    modifier: int
    advantage_status: AdvantageStatus = AdvantageStatus.NONE
    allow_critical: bool = True

    def expected_value(self):
        base_average = self.dice_count * (self.dice_value + 1) / 2 + self.modifier
        if self.advantage_status == AdvantageStatus.ADVANTAGE:
            advantage_average = (self.dice_value + 1) * (2 * self.dice_value + 1) / (3 * self.dice_value)
            return self.dice_count * advantage_average + self.modifier
        if self.advantage_status == AdvantageStatus.DISADVANTAGE:
            disadvantage_average = self.dice_value * (self.dice_value + 1) / (3 * self.dice_value)
            return self.dice_count * disadvantage_average + self.modifier
        return int(base_average)

    def roll_with_advantage(self) -> Tuple[int, str]:
        if self.advantage_status == AdvantageStatus.ADVANTAGE:
            rolls = [self.roll_single(), self.roll_single()]
            best_roll = max(rolls)
        elif self.advantage_status == AdvantageStatus.DISADVANTAGE:
            rolls = [self.roll_single(), self.roll_single()]
            best_roll = min(rolls)
        else:
            rolls = [self.roll_single()]
            best_roll = rolls[0]

        if self.allow_critical:
            if best_roll - self.modifier == 20:
                return best_roll, "critical_hit"
            elif best_roll - self.modifier == 1:
                return best_roll, "critical_failure"
        return best_roll, "normal"

    def roll_single(self) -> int:
        return sum(random.randint(1, self.dice_value) for _ in range(self.dice_count)) + self.modifier

    def roll(self, is_critical: bool = False) -> int:
        if is_critical:
            return sum(random.randint(1, self.dice_value) for _ in range(self.dice_count * 2)) + self.modifier
        return self.roll_single()


class Speed(BaseModel):
    walk: ModifiableValue
    fly: ModifiableValue = Field(default_factory=lambda: ModifiableValue(base_value=0))
    swim: ModifiableValue = Field(default_factory=lambda: ModifiableValue(base_value=0))
    burrow: ModifiableValue = Field(default_factory=lambda: ModifiableValue(base_value=0))
    climb: ModifiableValue = Field(default_factory=lambda: ModifiableValue(base_value=0))

    def get_speed(self, speed_type: str) -> int:
        return getattr(self, speed_type).get_value()

    def modify_speed(self, speed_type: str, source: str, value: int):
        getattr(self, speed_type).add_modifier(source, value)

    def remove_speed_modifier(self, speed_type: str, source: str):
        getattr(self, speed_type).remove_modifier(source)

class AbilityScore(BaseModel):
    ability: Ability
    score: ModifiableValue

    def get_score(self, stats_block: 'StatsBlock', target: Any = None) -> int:
        return self.score.get_value(stats_block, target)

    def get_modifier(self, stats_block: 'StatsBlock', target: Any = None) -> int:
        return (self.get_score(stats_block, target) - 10) // 2

    def get_advantage_status(self, stats_block: 'StatsBlock', target: Any = None) -> AdvantageStatus:
        return self.score.get_advantage_status(stats_block, target)

class AbilityScores(BaseModel):
    strength: AbilityScore = Field(AbilityScore(ability=Ability.STR, score=ModifiableValue(base_value=10)), description=strength_docstring)
    dexterity: AbilityScore = Field(AbilityScore(ability=Ability.DEX, score=ModifiableValue(base_value=10)), description=dexterity_docstring)
    constitution: AbilityScore = Field(AbilityScore(ability=Ability.CON, score=ModifiableValue(base_value=10)), description=constitution_docstring)
    intelligence: AbilityScore = Field(AbilityScore(ability=Ability.INT, score=ModifiableValue(base_value=10)), description=intelligence_docstring)
    wisdom: AbilityScore = Field(AbilityScore(ability=Ability.WIS, score=ModifiableValue(base_value=10)), description=wisdom_docstring)
    charisma: AbilityScore = Field(AbilityScore(ability=Ability.CHA, score=ModifiableValue(base_value=10)), description=charisma_docstring)

    def get_saving_throws(self, stats_block: 'StatsBlock') -> List['SavingThrow']:
        return [SavingThrow(ability=ability, bonus=getattr(self, ability.value.lower()).get_modifier(stats_block))
                for ability in Ability]

    def get_skill_bonuses(self, stats_block: 'StatsBlock') -> List['SkillBonus']:
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
        return [SkillBonus(skill=skill, bonus=getattr(self, skill_ability_map[skill].value.lower()).get_modifier(stats_block))
                for skill in Skills]

class AbilityCheck(BaseModel):
    ability: Skills
    difficulty_class: int
    contextual_effects: ContextualEffects = Field(default_factory=ContextualEffects)
    automatic_fails: Set[Skills] = Field(default_factory=set)

    def perform_check(self, stats_block: 'StatsBlock', target: Any = None) -> bool:
        if self.ability in self.automatic_fails:
            return False

        ability = next(ab for ab in Ability if ab.value.upper() == self.ability.value.split('_')[0])
        ability_score = getattr(stats_block.ability_scores, ability.value.lower())
        
        modifier = ability_score.get_modifier(stats_block, target)
        bonus = self.contextual_effects.compute_bonus(stats_block, target)
        total_modifier = modifier + bonus

        advantage_status = self.get_advantage_status(stats_block, target)
        
        dice = Dice(dice_count=1, dice_value=20, modifier=total_modifier, advantage_status=advantage_status)
        roll, _ = dice.roll_with_advantage()
        return roll >= self.difficulty_class

    def get_advantage_status(self, stats_block: 'StatsBlock', target: Any = None) -> AdvantageStatus:
        advantages = sum(1 for _, cond in self.contextual_effects.advantage_conditions if cond(stats_block, target))
        disadvantages = sum(1 for _, cond in self.contextual_effects.disadvantage_conditions if cond(stats_block, target))
        
        if advantages > disadvantages:
            return AdvantageStatus.ADVANTAGE
        elif disadvantages > advantages:
            return AdvantageStatus.DISADVANTAGE
        else:
            return AdvantageStatus.NONE

    def add_advantage_condition(self, source: str, condition: Callable[['StatsBlock', Any], bool]):
        self.contextual_effects.add_advantage_condition(source, condition)

    def add_disadvantage_condition(self, source: str, condition: Callable[['StatsBlock', Any], bool]):
        self.contextual_effects.add_disadvantage_condition(source, condition)

    def add_bonus(self, source: str, bonus: Callable[['StatsBlock', Any], int]):
        self.contextual_effects.add_bonus(source, bonus)

    def remove_effect(self, source: str):
        self.contextual_effects.remove_effect(source)


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
    concentration: bool = False
    type: DurationType = Field(DurationType.ROUNDS, description="The type of duration for the effect")
    has_advanced: bool = False  # Add this to track if the duration has been advanced

    def advance(self) -> bool:
        if not self.has_advanced:
            self.has_advanced = True
            return False  # Prevent the duration from advancing immediately
        if self.type in [DurationType.ROUNDS, DurationType.MINUTES, DurationType.HOURS]:
            if isinstance(self.time, int):
                print(f"Advancing duration: {self.time} remaining")
                if self.time > 0:
                    self.time -= 1
                return self.time <= 0  # Return True if the time has reached 0
        return False

    def is_expired(self) -> bool:
        return self.type != DurationType.INDEFINITE and (
            (isinstance(self.time, int) and self.time <= 0) or 
            (isinstance(self.time, str) and self.time.lower() == "expired")
        )



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







class Damage(BaseModel):
    dice: Dice
    type: DamageType

    def average_damage(self):
        return self.dice.expected_value()



class ActionEconomy(BaseModel):
    actions: ModifiableValue = Field(default_factory=lambda: ModifiableValue(base_value=1))
    bonus_actions: ModifiableValue = Field(default_factory=lambda: ModifiableValue(base_value=1))
    reactions: ModifiableValue = Field(default_factory=lambda: ModifiableValue(base_value=1))
    movement: ModifiableValue

    def __init__(self, speed: int):
        super().__init__(movement=ModifiableValue(base_value=speed))

    def reset(self):
        for attr in ['actions', 'bonus_actions', 'reactions', 'movement']:
            getattr(self, attr).base_value = getattr(self, attr).base_value

    def modify_actions(self, source: str, value: int):
        self.actions.add_static_modifier(source, value)

    def modify_bonus_actions(self, source: str, value: int):
        self.bonus_actions.add_static_modifier(source, value)

    def modify_reactions(self, source: str, value: int):
        self.reactions.add_static_modifier(source, value)

    def modify_movement(self, source: str, value: int):
        self.movement.add_static_modifier(source, value)

    def remove_actions_modifier(self, source: str):
        self.actions.remove_static_modifier(source)

    def remove_bonus_actions_modifier(self, source: str):
        self.bonus_actions.remove_static_modifier(source)

    def remove_reactions_modifier(self, source: str):
        self.reactions.remove_static_modifier(source)

    def remove_movement_modifier(self, source: str):
        self.movement.remove_static_modifier(source)