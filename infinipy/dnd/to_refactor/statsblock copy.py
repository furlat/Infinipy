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






class Condition(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str =Field("A generic description of the condition.")
    duration: Duration = Field(Duration(time=1, type=DurationType.ROUNDS))
    source_entity_id: Optional[str] = None

    def apply(self, stats_block: 'StatsBlock') -> None:
        print(f"Applying condition {self.name} to {stats_block.name}")
        pass

    def remove(self, stats_block: 'StatsBlock') -> None:
        print(f"Removing condition {self.name} from {stats_block.name}")
        pass

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

from typing import Callable, Tuple

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

class ArmorClass(BaseModel):
    base_ac: int
    contextual_modifiers: DirectionalContextualModifier = Field(default_factory=DirectionalContextualModifier)
    equipped_armor: Optional[Armor] = None
    equipped_shield: Optional[Shield] = None

    def compute_base_ac(self, ability_scores: AbilityScores) -> int:
        base_ac = 10 + ability_scores.dexterity.modifier
        if self.equipped_armor:
            base_ac = self.equipped_armor.base_ac
            if self.equipped_armor.dex_bonus:
                dex_bonus = ability_scores.dexterity.modifier
                if self.equipped_armor.max_dex_bonus is not None:
                    dex_bonus = min(dex_bonus, self.equipped_armor.max_dex_bonus)
                base_ac += dex_bonus
        if self.equipped_shield:
            base_ac += self.equipped_shield.ac_bonus
        self.base_ac = base_ac
        return self.base_ac

    def compute_ac(self, attacker: Optional[StatsBlock] = None) -> int:
        total_ac = self.base_ac
        if attacker:
            total_ac += self.contextual_modifiers.compute_self_bonus(attacker, self)
            total_ac -= self.contextual_modifiers.compute_opponent_bonus(attacker, self)
        return total_ac

    def give_advantage(self, attacker: StatsBlock) -> bool:
        return self.contextual_modifiers.gives_opponent_advantage(attacker, self)

    def give_disadvantage(self, attacker: StatsBlock) -> bool:
        return self.contextual_modifiers.gives_opponent_disadvantage(attacker, self)

    def add_self_bonus(self, attribute: str, bonus: Callable[['StatsBlock', 'StatsBlock'], int]):
        self.contextual_modifiers.add_self_bonus(attribute, bonus)

    def add_opponent_bonus(self, attribute: str, bonus: Callable[['StatsBlock', 'StatsBlock'], int]):
        self.contextual_modifiers.add_opponent_bonus(attribute, bonus)

    def add_self_advantage_condition(self, attribute: str, condition: Callable[['StatsBlock', 'StatsBlock'], bool]):
        self.contextual_modifiers.add_self_advantage(attribute, condition)

    def add_opponent_advantage_condition(self, attribute: str, condition: Callable[['StatsBlock', 'StatsBlock'], bool]):
        self.contextual_modifiers.add_opponent_advantage(attribute, condition)

    def add_self_disadvantage_condition(self, attribute: str, condition: Callable[['StatsBlock', 'StatsBlock'], bool]):
        self.contextual_modifiers.add_self_disadvantage(attribute, condition)

    def add_opponent_disadvantage_condition(self, attribute: str, condition: Callable[['StatsBlock', 'StatsBlock'], bool]):
        self.contextual_modifiers.add_opponent_disadvantage(attribute, condition)

    def equip_armor(self, armor: Armor):
        self.equipped_armor = armor

    def unequip_armor(self):
        self.equipped_armor = None

    def equip_shield(self, shield: Shield):
        self.equipped_shield = shield

    def unequip_shield(self):
        self.equipped_shield = None

class Attack(Action):
    attack_type: AttackType
    ability: Ability
    range: Range
    damage: List[Damage]
    weapon: Optional[Weapon] = None
    additional_effects: Union[str, None] = None
    advantage_tracker: AdvantageTracker = Field(default_factory=AdvantageTracker)
    blocked_targets: Set[str] = Field(default_factory=set)
    is_critical_hit: bool = False
    contextual_modifiers: DirectionalContextualModifier = Field(default_factory=DirectionalContextualModifier)

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

    def can_attack(self, target_id: str) -> bool:
        return target_id not in self.blocked_targets

    def add_blocked_target(self, target_id: str):
        self.blocked_targets.add(target_id)

    def remove_blocked_target(self, target_id: str):
        self.blocked_targets.discard(target_id)

    def add_contextual_advantage(self, attribute: str, condition: Callable[['StatsBlock', 'StatsBlock'], bool]):
        self.contextual_modifiers.add_self_advantage(attribute, condition)

    def add_contextual_disadvantage(self, attribute: str, condition: Callable[['StatsBlock', 'StatsBlock'], bool]):
        self.contextual_modifiers.add_self_disadvantage(attribute, condition)

    def add_contextual_bonus(self, attribute: str, bonus: Callable[['StatsBlock', 'StatsBlock'], int]):
        self.contextual_modifiers.add_self_bonus(attribute, bonus)

    def roll_to_hit(self, target: StatsBlock, verbose: bool = False) -> Union[bool, Tuple[bool, Dict[str, Any]]]:
        self.advantage_tracker.reset()  # Ensure the tracker is reset at the beginning of each attack roll

        # Check for conditions on the attacker
        if self.contextual_modifiers.gives_self_disadvantage(self.stats_block, target):
            self.advantage_tracker.add_disadvantage(self.stats_block)
        if self.contextual_modifiers.gives_self_advantage(self.stats_block, target):
            self.advantage_tracker.add_advantage(self.stats_block)

        # Check for conditions on the target
        if target.armor_class.give_disadvantage(self.stats_block):
            self.advantage_tracker.add_disadvantage(self.stats_block)
        if target.armor_class.give_advantage(self.stats_block):
            self.advantage_tracker.add_advantage(self.stats_block)

        self_bonus = self.contextual_modifiers.compute_self_bonus(self.stats_block, target)
        opponent_bonus = self.contextual_modifiers.compute_opponent_bonus(self.stats_block, target)
        
        dice = Dice(
            dice_count=1,
            dice_value=20,
            modifier=self.hit_bonus + self_bonus - opponent_bonus,
            advantage_status=self.advantage_tracker.status
        )
        roll, roll_status = dice.roll_with_advantage()

        self.is_critical_hit = roll_status == "critical_hit"
        hit = roll >= target.armor_class.compute_ac(self.stats_block)

        if verbose:
            details = {
                "hit": hit,
                "roll": roll,
                "roll_status": roll_status,
                "self_bonus": self_bonus,
                "opponent_bonus": opponent_bonus,
                "advantage_status": self.advantage_tracker.status,
                "armor_class": target.armor_class.compute_ac(self.stats_block),
                "is_critical_hit": self.is_critical_hit,
                "contextual_self_disadvantages": self.contextual_modifiers.self_disadvantages,
                "contextual_self_advantages": self.contextual_modifiers.self_advantages
            }
            return hit, details

        return hit



    def roll_damage(self) -> int:
        total_damage = 0
        for damage in self.damage:
            dice = Dice(
                dice_count=damage.dice.dice_count,
                dice_value=damage.dice.dice_value,
                modifier=damage.dice.modifier,
                advantage_status=self.advantage_tracker.status
            )
            total_damage += dice.roll(is_critical=self.is_critical_hit)
        return total_damage





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


class StatsBlock(BaseModel):
    name: str = Field(..., description="name of the creature")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="unique identifier for the creature")
    size: Size = Field(..., description=size_docstring)
    type: MonsterType = Field(..., description=type_docstring)
    alignment: Alignment = Field(..., description=alignment_docstring)
    ability_scores: AbilityScores = Field(AbilityScores(), description=ability_scores_docstring)
    speed: Speed = Field(Speed(walk=ModifiableValue(base_value=30)), description=speed_docstring)
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
    armor_class: ArmorClass = Field(default_factory=lambda: ArmorClass(base_ac=10))
    weapons: List[Weapon] = Field(default_factory=list)
    hit_dice: Dice
    hit_point_bonus: int = Field(0, description="Bonus to max hit points from various sources")
    current_hit_points: int = Field(0)
    computed_passive_perception: ModifiableValue = Field(default_factory=lambda: ModifiableValue(base_value=0))
    action_economy: ActionEconomy = Field(default_factory=lambda: ActionEconomy(speed=30))
    active_conditions: Dict[Tuple[str, str], Condition] = Field(default_factory=dict)
    modifier_immunity: List[str] = Field(default_factory=list)
    line_of_sight: Set[str] = Field(default_factory=set)

    def __init__(self, **data):
        super().__init__(**data)
        self.add_default_actions()
        if self.current_hit_points == 0:
            self.current_hit_points = self.max_hit_points
        self._recompute_fields()

    def add_default_actions(self):
        self.add_action(Dodge(stats_block=self))
        self.add_action(Disengage(stats_block=self))
        self.add_action(Dash(stats_block=self))
        self.add_action(Hide(stats_block=self))
        self.add_action(Help(stats_block=self))

    def refresh_line_of_sight(self, visible_entities: Set[str]):
        self.line_of_sight = visible_entities

    def is_in_line_of_sight(self, entity_id: str) -> bool:
        return entity_id in self.line_of_sight

    def update_conditions(self):
        expired_conditions = []
        for key, condition in self.active_conditions.items():
            if condition.duration.advance():
                expired_conditions.append(key)
        
        for key in expired_conditions:
            print(f"Condition {key[0]} with ID {key[1]} expired on {self.name}")
            self.remove_condition(*key)

    def apply_active_conditions(self):
        for condition in self.active_conditions.values():
            condition.apply(self)

    def _recompute_fields(self):
        self.armor_class.compute_base_ac(self.ability_scores)
        self._compute_passive_perception()
        self.action_economy.movement.base_value = self.speed.walk.get_value()
        self.action_economy.reset()
        for action in self.actions:
            if isinstance(action, Attack):
                action.advantage_tracker.reset()
        self.apply_active_conditions()

    @computed_field
    def max_hit_points(self) -> int:
        con_modifier = self.ability_scores.constitution.modifier
        average_hp = (self.hit_dice.expected_value()) + \
                     (con_modifier * self.hit_dice.dice_count) + \
                     self.hit_point_bonus
        return max(1, int(average_hp))

    def apply_condition(self, condition: Condition):
        if condition.name in self.modifier_immunity:
            return
        key = (condition.name, condition.id)
        if key not in self.active_conditions:
            print(f"Applying condition {condition.name} with ID {condition.id} to {self.name}")
            self.active_conditions[key] = condition
            # condition.apply(self)
            self._recompute_fields()  # Recompute fields only if a new condition is applied

    def remove_condition(self, condition_name: str, condition_id: str):
        key = (condition_name, condition_id)
        if key in self.active_conditions:
            print(f"Removing condition {condition_name} with ID {condition_id} from {self.name}")
            condition = self.active_conditions.pop(key)
            condition.remove(self)
            self._recompute_fields()  # Recompute fields after condition is removed

    def get_conditions_by_name(self, name: str) -> List[Condition]:
        return [cond for key, cond in self.active_conditions.items() if key[0] == name]

    def get_condition_by_id(self, condition_id: str) -> Optional[Condition]:
        for key, cond in self.active_conditions.items():
            if key[1] == condition_id:
                return cond
        return None

    @computed_field
    def proficiency_bonus(self) -> int:
        return max(2, ((self.challenge - 1) // 4) + 2)

    @computed_field
    def armor_class_value(self) -> int:
        return self.armor_class.base_ac

    @computed_field
    def initiative(self) -> int:
        return self.ability_scores.dexterity.modifier

    @computed_field
    def passive_perception(self) -> int:
        return self.computed_passive_perception.total_value

    def _compute_passive_perception(self):
        perception_bonus = next((skill.bonus for skill in self.skills if skill.skill == Skills.PERCEPTION), 0)
        self.computed_passive_perception.base_value = 10 + self.ability_scores.wisdom.modifier + perception_bonus

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
        self.armor_class.equip_armor(armor)
        self._recompute_fields()

    def unequip_armor(self):
        self.armor_class.unequip_armor()
        self._recompute_fields()

    def equip_shield(self, shield: Shield):
        self.armor_class.equip_shield(shield)
        self._recompute_fields()

    def unequip_shield(self):
        self.armor_class.unequip_shield()
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

        targeting = Targeting(
            type=TargetType.ONE_TARGET,
            range=weapon.range.normal,
            line_of_sight=True,
            requirement=TargetRequirementType.ANY
        )

        attack = Attack(
            name=weapon.name,
            description=f"{weapon.attack_type.value} Attack with {weapon.name}",
            cost=[ActionCost(type=ActionType.ACTION, cost=1)],
            limited_usage=None,
            attack_type=weapon.attack_type,
            ability=ability,
            range=weapon.range,
            damage=[weapon.damage],
            targeting=targeting,
            stats_block=self,
            weapon=weapon
        )
        self.add_action(attack)

    def update_ability_scores(self, new_ability_scores: AbilityScores):
        self.ability_scores = new_ability_scores
        self._recompute_fields()
        for action in self.actions + self.reactions + self.legendary_actions + self.lair_actions:
            if isinstance(action, Attack):
                action.hit_bonus = action.hit_bonus
                action.average_damage = action.average_damage

    def safe_update(self, **kwargs):
        updatable_fields = set(self.model_fields.keys()) - set(self.__computed_fields__)
        for key, value in kwargs.items():
            if key in updatable_fields:
                if isinstance(getattr(self, key), ModifiableValue):
                    getattr(self, key).base_value = value
                else:
                    setattr(self, key, value)
        self._recompute_fields()

    def take_damage(self, damage: int):
        self.current_hit_points = max(0, self.current_hit_points - damage)

    def heal(self, healing: int):
        self.current_hit_points = min(self.max_hit_points, self.current_hit_points + healing)

    def add_hit_point_bonus(self, bonus: int):
        self.hit_point_bonus += bonus
        self._recompute_fields()

    def remove_hit_point_bonus(self, bonus: int):
        self.hit_point_bonus -= bonus
        self._recompute_fields()


## condition effects
# | **Status Effect**       | **Description**                                                                                             | **Required Components in Submodels**                                                                                        |
# |-------------------------|-------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------|
# | **Blinded**             | Cannot see, automatically fails any check requiring sight, attack rolls have disadvantage.                  | `Attack`: Add ability to apply disadvantage; `AbilityCheck`: Add failure condition for sight-related checks.                |
# | **Charmed**             | Cannot attack the charmer, the charmer has advantage on social interactions.                                | `Attack`: Add logic to prevent attacking charmer; `AbilityCheck`: Add advantage for social interactions with charmer.       |
# | **Deafened**            | Cannot hear, automatically fails any check requiring hearing.                                               | `AbilityCheck`: Add failure condition for hearing-related checks.                                                           |
# | **Frightened**          | Disadvantage on ability checks and attack rolls while the source of fear is in sight.                       | `Attack`: Add ability to apply disadvantage; `AbilityCheck`: Add ability to apply disadvantage.                              |
# | **Grappled**            | Speed becomes 0, can't benefit from any bonus to speed.                                                     | `Speed`: Add logic to set speed to 0.                                                                                       |
# | **Incapacitated**       | Cannot take actions or reactions.                                                                           | `ActionEconomy`: Add logic to block actions and reactions.                                                                  |
# | **Invisible**           | Impossible to see without special sense, attacks against have disadvantage, attacks have advantage.         | `Attack`: Add ability to apply advantage/disadvantage.                                                                      |
# | **Paralyzed**           | Incapacitated, can't move or speak, automatically fails Strength and Dexterity saves, attacks have advantage. | `ActionEconomy`: Add logic to block actions and reactions; `Speed`: Add logic to set speed to 0; `SavingThrow`: Add failure condition. |
# | **Petrified**           | Transformed into solid inanimate substance, incapacitated, and unaware of surroundings.                     | `ActionEconomy`: Add logic to block actions and reactions; `Speed`: Add logic to set speed to 0; `SavingThrow`: Add failure condition. |
# | **Poisoned**            | Disadvantage on attack rolls and ability checks.                                                            | `Attack`: Add ability to apply disadvantage; `AbilityCheck`: Add ability to apply disadvantage.                              |
# | **Prone**               | Disadvantage on attack rolls, attacks within 5 feet have advantage, others have disadvantage.               | `Attack`: Add ability to apply advantage/disadvantage.                                                                      |
# | **Restrained**          | Speed becomes 0, attack rolls have disadvantage, Dexterity saves have disadvantage.                         | `Speed`: Add logic to set speed to 0; `Attack`: Add ability to apply disadvantage; `SavingThrow`: Add ability to apply disadvantage. |
# | **Stunned**             | Incapacitated, can't move, can speak only falteringly.                                                      | `ActionEconomy`: Add logic to block actions and reactions; `Speed`: Add logic to set speed to 0; `SavingThrow`: Add failure condition. |
# | **Unconscious**         | Incapacitated, can't move or speak, unaware of surroundings, drops held items, falls prone.                | `ActionEconomy`: Add logic to block actions and reactions; `Speed`: Add logic to set speed to 0; `SavingThrow`: Add failure condition. |
# | **Dodging**             | Attacks against have disadvantage, Dexterity saves have advantage.                                          | `Attack`: Add ability to apply disadvantage; `SavingThrow`: Add ability to apply advantage.                                  |
# | **Dashing**             | Movement increases by an additional speed.                                                                  | `Speed`: Add logic to increase movement.                                                                                    |
# | **Hiding**              | Makes Dexterity (Stealth) checks to hide.                                                                   | `AbilityCheck`: Add logic for hiding mechanic.                                                                              |
# | **Helping**             | Lends aid to another creature, giving advantage on next ability check or attack roll.                       | `Attack`: Add ability to apply advantage; `AbilityCheck`: Add ability to apply advantage.                                   |

class Blinded(Condition):
    name: str = Field("Blinded")

    def apply(self, stats_block: 'StatsBlock') -> None:
        for action in stats_block.actions:
            if isinstance(action, Attack):
                action.contextual_modifiers.add_self_disadvantage("Blinded", lambda src, tgt: True)

    def remove(self, stats_block: 'StatsBlock') -> None:
        for action in stats_block.actions:
            if isinstance(action, Attack):
                action.contextual_modifiers.self_disadvantages = [
                    condition for condition in action.contextual_modifiers.self_disadvantages 
                    if condition[0] != "Blinded"
                ]







class Charmed(Condition):
    name: str = "Charmed"

    def apply(self, stats_block: 'StatsBlock') -> None:
        for action in stats_block.actions:
            if isinstance(action, Attack):
                action.add_blocked_target(self.source_entity_id)

    def remove(self, stats_block: 'StatsBlock') -> None:
        for action in stats_block.actions:
            if isinstance(action, Attack):
                action.remove_blocked_target(self.source_entity_id)

class Deafened(Condition):
    name: str = "Deafened"

    def apply(self, stats_block: 'StatsBlock') -> None:
        for action in stats_block.actions:
            if isinstance(action, AbilityCheck) and action.ability in HEARING_DEPENDENT_ABILITIES:
                action.automatic_fails.add(action.ability)

    def remove(self, stats_block: 'StatsBlock') -> None:
        for action in stats_block.actions:
            if isinstance(action, AbilityCheck) and action.ability in HEARING_DEPENDENT_ABILITIES:
                action.automatic_fails.discard(action.ability)

class Frightened(Condition):
    name: str = "Frightened"

    def apply(self, stats_block: 'StatsBlock') -> None:
        if stats_block.is_in_line_of_sight(self.source_entity_id):
            for action in stats_block.actions:
                if isinstance(action, Attack):
                    action.contextual_modifiers.add_self_disadvantage("Frightened", lambda src, tgt: True)
                if isinstance(action, AbilityCheck):
                    action.set_disadvantage()

    def remove(self, stats_block: 'StatsBlock') -> None:
        for action in stats_block.actions:
            if isinstance(action, Attack):
                action.contextual_modifiers.self_disadvantages = [
                    condition for condition in action.contextual_modifiers.self_disadvantages 
                    if condition[0] != "Frightened"
                ]
            if isinstance(action, AbilityCheck):
                action.set_advantage()

    def update(self, stats_block: 'StatsBlock') -> None:
        if stats_block.is_in_line_of_sight(self.source_entity_id):
            self.apply(stats_block)
        else:
            self.remove(stats_block)


class Grappled(Condition):
    name: str = "Grappled"

    def apply(self, stats_block: 'StatsBlock') -> None:
        for speed_type in ["walk", "fly", "swim", "burrow", "climb"]:
            stats_block.speed.modify_speed(speed_type, self.id, -stats_block.speed.get_speed(speed_type))

    def remove(self, stats_block: 'StatsBlock') -> None:
        for speed_type in ["walk", "fly", "swim", "burrow", "climb"]:
            stats_block.speed.remove_speed_modifier(speed_type, self.id)


class Incapacitated(Condition):
    name: str = "Incapacitated"

    def apply(self, stats_block: 'StatsBlock') -> None:
        stats_block.action_economy.modify_actions(self.id, -stats_block.action_economy.actions.base_value)
        stats_block.action_economy.modify_reactions(self.id, -stats_block.action_economy.reactions.base_value)

    def remove(self, stats_block: 'StatsBlock') -> None:
        stats_block.action_economy.remove_actions_modifier(self.id)
        stats_block.action_economy.remove_reactions_modifier(self.id)
