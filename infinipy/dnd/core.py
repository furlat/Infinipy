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

class DurationType(str, Enum):
    INSTANTANEOUS = "instantaneous"
    ROUNDS = "rounds"
    MINUTES = "minutes"
    HOURS = "hours"
    INDEFINITE = "indefinite"

HEARING_DEPENDENT_ABILITIES = {Skills.PERCEPTION, Skills.PERFORMANCE, Skills.INSIGHT}

class AdvantageTracker(BaseModel):
    counter: int = 0

    def add_advantage(self, stats_block: 'StatsBlock'):
        if 'Advantage' not in stats_block.modifier_immunity:
            self.counter += 1

    def add_disadvantage(self, stats_block: 'StatsBlock'):
        if 'Disadvantage' not in stats_block.modifier_immunity:
            self.counter -= 1

    def reset(self):
        self.counter = 0

    @property
    def status(self) -> AdvantageStatus:
        if self.counter > 0:
            return AdvantageStatus.ADVANTAGE
        elif self.counter < 0:
            return AdvantageStatus.DISADVANTAGE
        else:
            return AdvantageStatus.NONE

## base models
class Modifier(BaseModel):
    value: int
    source: str
    duration: int = -1  # -1 for permanent, otherwise number of rounds


class ModifiableValue(BaseModel):
    base_value: int
    modifiers: Dict[str, int] = Field(default_factory=dict)

    @property
    def total_value(self) -> int:
        return self.base_value + sum(self.modifiers.values())

    def add_modifier(self, source: str, value: int):
        self.modifiers[source] = value

    def remove_modifier(self, source: str):
        self.modifiers.pop(source, None)

    def get_value(self) -> int:
        return max(0, self.total_value)  # Ensure the value doesn't go below 0

    # We don't need an update_modifiers method as modifiers are updated when added or removed

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

    @computed_field
    def modifier(self) -> int:
        return (self.score.total_value - 10) // 2

class AbilityScores(BaseModel):
    strength: AbilityScore = Field(AbilityScore(ability=Ability.STR, score=ModifiableValue(base_value=10)), description=strength_docstring)
    dexterity: AbilityScore = Field(AbilityScore(ability=Ability.DEX, score=ModifiableValue(base_value=10)), description=dexterity_docstring)
    constitution: AbilityScore = Field(AbilityScore(ability=Ability.CON, score=ModifiableValue(base_value=10)), description=constitution_docstring)
    intelligence: AbilityScore = Field(AbilityScore(ability=Ability.INT, score=ModifiableValue(base_value=10)), description=intelligence_docstring)
    wisdom: AbilityScore = Field(AbilityScore(ability=Ability.WIS, score=ModifiableValue(base_value=10)), description=wisdom_docstring)
    charisma: AbilityScore = Field(AbilityScore(ability=Ability.CHA, score=ModifiableValue(base_value=10)), description=charisma_docstring)

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

class AbilityCheck(BaseModel):
    ability: Skills
    difficulty_class: int
    advantage_tracker: AdvantageTracker = Field(default_factory=AdvantageTracker)
    automatic_fails: Set[Skills] = Field(default_factory=set)

    def perform_check(self, stats_block: 'StatsBlock') -> bool:
        if self.ability in self.automatic_fails:
            return False

        ability_modifier = getattr(stats_block.ability_scores, self.ability.value.lower()).modifier
        dice = Dice(dice_count=1, dice_value=20, modifier=ability_modifier, advantage_status=self.advantage_tracker.status)
        roll, _ = dice.roll_with_advantage()
        return roll >= self.difficulty_class

    def set_disadvantage(self):
        self.advantage_tracker.add_disadvantage(None)

    def set_advantage(self):
        self.advantage_tracker.add_advantage(None)


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




class Damage(BaseModel):
    dice: Dice
    type: DamageType

    def average_damage(self):
        return self.dice.expected_value()





class DirectionalContextualModifier(BaseModel):
    self_bonuses: List[Tuple[str, Callable[['StatsBlock', 'StatsBlock'], int]]] = Field(default_factory=list)
    opponent_bonuses: List[Tuple[str, Callable[['StatsBlock', 'StatsBlock'], int]]] = Field(default_factory=list)
    self_advantages: List[Tuple[str, Callable[['StatsBlock', 'StatsBlock'], bool]]] = Field(default_factory=list)
    opponent_advantages: List[Tuple[str, Callable[['StatsBlock', 'StatsBlock'], bool]]] = Field(default_factory=list)
    self_disadvantages: List[Tuple[str, Callable[['StatsBlock', 'StatsBlock'], bool]]] = Field(default_factory=list)
    opponent_disadvantages: List[Tuple[str, Callable[['StatsBlock', 'StatsBlock'], bool]]] = Field(default_factory=list)

    def add_self_bonus(self, attribute: str, bonus: Callable[['StatsBlock', 'StatsBlock'], int]):
        self.self_bonuses.append((attribute, bonus))

    def add_opponent_bonus(self, attribute: str, bonus: Callable[['StatsBlock', 'StatsBlock'], int]):
        self.opponent_bonuses.append((attribute, bonus))

    def add_self_advantage(self, attribute: str, condition: Callable[['StatsBlock', 'StatsBlock'], bool]):
        self.self_advantages.append((attribute, condition))

    def add_opponent_advantage(self, attribute: str, condition: Callable[['StatsBlock', 'StatsBlock'], bool]):
        self.opponent_advantages.append((attribute, condition))

    def add_self_disadvantage(self, attribute: str, condition: Callable[['StatsBlock', 'StatsBlock'], bool]):
        self.self_disadvantages.append((attribute, condition))

    def add_opponent_disadvantage(self, attribute: str, condition: Callable[['StatsBlock', 'StatsBlock'], bool]):
        self.opponent_disadvantages.append((attribute, condition))

    def compute_self_bonus(self, source: 'StatsBlock', target: 'StatsBlock') -> int:
        total_bonus = 0
        for attribute, bonus in self.self_bonuses:
            total_bonus += bonus(source, target)
        return total_bonus

    def compute_opponent_bonus(self, source: 'StatsBlock', target: 'StatsBlock') -> int:
        total_bonus = 0
        for attribute, bonus in self.opponent_bonuses:
            total_bonus += bonus(source, target)
        return total_bonus

    def gives_self_advantage(self, source: 'StatsBlock', target: 'StatsBlock') -> bool:
        for attribute, condition in self.self_advantages:
            if condition(source, target):
                return True
        return False

    def gives_opponent_advantage(self, source: 'StatsBlock', target: 'StatsBlock') -> bool:
        for attribute, condition in self.opponent_advantages:
            if condition(source, target):
                return True
        return False

    def gives_self_disadvantage(self, source: 'StatsBlock', target: 'StatsBlock') -> bool:
        for attribute, condition in self.self_disadvantages:
            if condition(source, target):
                return True
        return False

    def gives_opponent_disadvantage(self, source: 'StatsBlock', target: 'StatsBlock') -> bool:
        for attribute, condition in self.opponent_disadvantages:
            if condition(source, target):
                return True
        return False


class ActionEconomy(BaseModel):
    actions: ModifiableValue = Field(default_factory=lambda: ModifiableValue(base_value=1))
    bonus_actions: ModifiableValue = Field(default_factory=lambda: ModifiableValue(base_value=1))
    reactions: ModifiableValue = Field(default_factory=lambda: ModifiableValue(base_value=1))
    movement: ModifiableValue

    def __init__(self, speed: int):
        super().__init__(movement=ModifiableValue(base_value=speed))

    def reset(self):
        for attr in ['actions', 'bonus_actions', 'reactions', 'movement']:
            getattr(self, attr).modifiers.clear()

    def modify_actions(self, source: str, value: int):
        self.actions.add_modifier(source, value)

    def modify_bonus_actions(self, source: str, value: int):
        self.bonus_actions.add_modifier(source, value)

    def modify_reactions(self, source: str, value: int):
        self.reactions.add_modifier(source, value)

    def modify_movement(self, source: str, value: int):
        self.movement.add_modifier(source, value)

    def remove_actions_modifier(self, source: str):
        self.actions.remove_modifier(source)

    def remove_bonus_actions_modifier(self, source: str):
        self.bonus_actions.remove_modifier(source)

    def remove_reactions_modifier(self, source: str):
        self.reactions.remove_modifier(source)

    def remove_movement_modifier(self, source: str):
        self.movement.remove_modifier(source)