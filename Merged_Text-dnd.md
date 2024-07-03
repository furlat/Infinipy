# Combined Text Dir from dnd

- Full filepath to the merged directory: `C:\Users\Tommaso\Documents\Dev\Infinipy\infinipy\dnd`

- Created: `2024-07-03T11:56:44.296466`

## init



---

## actions

from pydantic import BaseModel, Field, computed_field

from typing import List, Optional, Union, Dict, Any, Tuple, Set, Callable, TYPE_CHECKING
from enum import Enum
from infinipy.dnd.core import ModifiableValue, Dice, Ability, DamageType, Damage, Range, RangeType, ShapeType, TargetType, TargetRequirementType, StatusEffect, Duration, LimitedUsage, UsageType, RechargeType, ActionType, ActionCost, Targeting, AdvantageTracker, DirectionalContextualModifier
from infinipy.dnd.equipment import  Weapon, Armor, WeaponProperty, ArmorType


if TYPE_CHECKING:
    from infinipy.dnd.statsblock import StatsBlock

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

    def roll_to_hit(self, target: 'StatsBlock', verbose: bool = False) -> Union[bool, Tuple[bool, Dict[str, Any]]]:
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


---

## conditions

from pydantic import BaseModel, Field
from typing import Optional, TYPE_CHECKING
import uuid
from infinipy.dnd.core import Duration, DurationType, AbilityCheck, HEARING_DEPENDENT_ABILITIES
from infinipy.dnd.actions import Attack


if TYPE_CHECKING:
    from infinipy.dnd.statsblock import StatsBlock

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


---

## core

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

---

## docstrings

size_docstring: str = """A monster can be Tiny, Small, Medium, Large, Huge, or Gargantuan. Table: Size Categories shows how much space a creature of a particular size controls in combat."""

modifying_creatures_docstring: str = """Despite the versatile collection of monsters in this book, you might be at a loss when it comes to finding the perfect creature for part of an adventure. Feel free to tweak an existing creature to make it into something more useful for you, perhaps by borrowing a trait or two from a different monster or by using a variant or template, such as the ones in this book. Keep in mind that modifying a monster, including when you apply a template to it, might change its challenge rating."""

type_docstring: str = """A monster’s type speaks to its fundamental nature. Certain spells, magic items, class features, and other effects in the game interact in special ways with creatures of a particular type. For example, an arrow of dragon slaying deals extra damage not only to dragons but also other creatures of the dragon type, such as dragon turtles and wyverns.

The game includes the following monster types, which have no rules of their own:

- **Aberration**: Aberrations are utterly alien beings. Many of them have innate magical abilities drawn from the creature’s alien mind rather than the mystical forces of the world.
- **Beast**: Beasts are nonhumanoid creatures that are a natural part of the fantasy ecology. Some of them have magical powers, but most are unintelligent and lack any society or language. Beasts include all varieties of ordinary animals, dinosaurs, and giant versions of animals.
- **Celestial**: Celestials are creatures native to the Upper Planes. Many of them are the servants of deities, employed as messengers or agents in the mortal realm and throughout the planes. Celestials are good by nature, so the exceptional celestial who strays from a good alignment is a horrifying rarity. Celestials include angels, couatls, and pegasi.
- **Construct**: Constructs are made, not born. Some are programmed by their creators to follow a simple set of instructions, while others are imbued with sentience and capable of independent thought. Golems are the iconic constructs. Many creatures native to the outer plane of Mechanus, such as modrons, are constructs shaped from the raw material of the plane by the will of more powerful creatures.
- **Dragon**: Dragons are large reptilian creatures of ancient origin and tremendous power. True dragons, including the good metallic dragons and the evil chromatic dragons, are highly intelligent and have innate magic. Also in this category are creatures distantly related to true dragons, but less powerful, less intelligent, and less magical, such as wyverns and pseudodragons.
- **Elemental**: Elementals are creatures native to the elemental planes. Some creatures of this type are little more than animate masses of their respective elements, including the creatures simply called elementals. Others have biological forms infused with elemental energy. The races of genies, including djinn and efreet, form the most important civilizations on the elemental planes. Other elemental creatures include azers, invisible stalkers, and water weirds.
- **Fey**: Fey are magical creatures closely tied to the forces of nature. They dwell in twilight groves and misty forests. In some worlds, they are closely tied to the Plane of Faerie. Some are also found in the Outer Planes, particularly the planes of Arborea and the Beastlands. Fey include dryads, pixies, and satyrs.
- **Fiend**: Fiends are creatures of wickedness that are native to the Lower Planes. A few are the servants of deities, but many more labor under the leadership of archdevils and demon princes. Evil priests and mages sometimes summon fiends to the material world to do their bidding. If an evil celestial is a rarity, a good fiend is almost inconceivable. Fiends include demons, devils, hell hounds, rakshasas, and yugoloths.
- **Giant**: Giants tower over humans and their kind. They are humanlike in shape, though some have multiple heads (ettins) or deformities (fomorians). The six varieties of true giant are hill giants, stone giants, frost giants, fire giants, cloud giants, and storm giants. Besides these, creatures such as ogres and trolls are giants.
- **Goblinoids**: Almost as numerous but far more savage and brutal, and almost uniformly evil, are the races of goblinoids (goblins, hobgoblins, and bugbears), orcs, gnolls, lizardfolk, and kobolds.
- **Humanoid**: Humanoids are the main peoples of a fantasy gaming world, both civilized and savage, including humans and a tremendous variety of other species. They have language and culture, few if any innate magical abilities (though most humanoids can learn spellcasting), and a bipedal form. The most common humanoid races are the ones most suitable as player characters: humans, dwarves, elves, and halflings.
- **Monstrosity**: Monstrosities are monsters in the strictest sense—frightening creatures that are not ordinary, not truly natural, and almost never benign. Some are the results of magical experimentation gone awry (such as owlbears), and others are the product of terrible curses (including minotaurs and yuan-ti). They defy categorization, and in some sense serve as a catch-all category for creatures that don’t fit into any other type.
- **Ooze**: Oozes are gelatinous creatures that rarely have a fixed shape. They are mostly subterranean, dwelling in caves and dungeons and feeding on refuse, carrion, or creatures unlucky enough to get in their way. Black puddings and gelatinous cubes are among the most recognizable oozes.
- **Plant**: Plants in this context are vegetable creatures, not ordinary flora. Most of them are ambulatory, and some are carnivorous. The quintessential plants are the shambling mound and the treant. Fungal creatures such as the gas spore and the myconid also fall into this category.
- **Undead**: Undead are once-living creatures brought to a horrifying state of undeath through the practice of necromantic magic or some unholy curse. Undead include walking corpses, such as vampires and zombies, as well as bodiless spirits, such as ghosts and specters.
"""

tags_docstring: str = """A monster might have one or more tags appended to its type, in parentheses. For example, an orc has the humanoid (orc) type. The parenthetical tags provide additional categorization for certain creatures. The tags have no rules of their own, but something in the game, such as a magic item, might refer to them. For instance, a spear that is especially effective at fighting demons would work against any monster that has the demon tag."""

ability_scores_docstring: str = """Every monster has six ability scores (Strength, Dexterity, Constitution, Intelligence, Wisdom, and Charisma) and corresponding modifiers."""

strength_docstring: str = """Strength measures bodily power, athletic training, and the extent to which you can exert raw physical force. A creature with a Strength score of 0 is incapable of moving and is effectively immobile (but not unconscious)."""

dexterity_docstring: str = """Dexterity measures agility, reflexes, and balance. A creature with a Dexterity score of 0 is incapable of moving and is effectively immobile (but not unconscious)."""

constitution_docstring: str = """Constitution measures health, stamina, and vital force. A Constitution score of 0 means that the creature is dead."""

intelligence_docstring: str = """Intelligence measures mental acuity, accuracy of recall, and the ability to reason. Creatures of animal-level instinct have Intelligence scores of 1 or 2. Any creature capable of understanding speech has a score of at least 3."""

wisdom_docstring: str = """Wisdom reflects how attuned you are to the world around you and represents perceptiveness and intuition."""

charisma_docstring: str = """Charisma measures your ability to interact effectively with others. It includes such factors as confidence and eloquence, and it can represent a charming or commanding personality."""

alignment_docstring: str = """ A monster’s alignment provides a clue to its disposition and how it behaves in a roleplaying or combat situation. For example, a chaotic evil monster might be difficult to reason with and might attack characters on sight, whereas a neutral monster might be willing to negotiate.

The alignment specified in a monster’s stat block is the default. Feel free to depart from it and change a monster’s alignment to suit the needs of your campaign. If you want a good-aligned green dragon or an evil storm giant, there’s nothing stopping you.

Some creatures can have any alignment. In other words, you choose the monster’s alignment. Some monster’s alignment entry indicates a tendency or aversion toward law, chaos, good, or evil. For example, a berserker can be any chaotic alignment (chaotic good, chaotic neutral, or chaotic evil), as befits its wild nature.

Many creatures of low intelligence have no comprehension of law or chaos, good or evil. They don’t make moral or ethical choices, but rather act on instinct. These creatures are unaligned, which means they don’t have an alignment. """


armor_class_docstring: str = """ A monster that wears armor or carries a shield has an Armor Class (AC) that takes its armor, shield, and Dexterity into account. Otherwise, a monster’s AC is based on its Dexterity modifier and natural armor, if any. If a monster has natural armor, wears armor, or carries a shield, this is noted in parentheses after its AC value. """

hit_points_docstring: str = """
A monster usually dies or is destroyed when it drops to 0 hit points.

A monster’s hit points are presented both as a die expression and as an average number. For example, a monster with 2d8 hit points has 9 hit points on average (2 × 4½).

A monster’s size determines the die used to calculate its hit points, as shown in Table: Hit Dice by Size.

### Table: Hit Dice by Size
| Monster Size | Hit Die | Average HP per Die |
|--------------|---------|--------------------|
| Tiny         | d4      | 2½                 |
| Small        | d6      | 3½                 |
| Medium       | d8      | 4½                 |
| Large        | d10     | 5½                 |
| Huge         | d12     | 6½                 |
| Gargantuan   | d20     | 10½                |

A monster’s Constitution modifier also affects the number of hit points it has. Its Constitution modifier is multiplied by the number of Hit Dice it possesses, and the result is added to its hit points. For example, if a monster has a Constitution of 12 (+1 modifier) and 2d8 Hit Dice, it has 2d8 + 2 hit points (average 11).
"""


speed_docstring: str = """ A monster’s speed tells you how far it can move on its turn.

All creatures have a walking speed, simply called the monster’s speed. Creatures that have no form of ground-based locomotion have a walking speed of 0 feet.

Some creatures have one or more of the following additional movement modes."""

burrow_docstring: str =  """ A monster that has a burrowing speed can use that speed to move through sand, earth, mud, or ice. A monster can’t burrow through solid rock unless it has a special trait that allows it to do so.
"""

climb_docstring: str = """ A monster that has a climbing speed can use all or part of its movement to move on vertical surfaces. The monster doesn’t need to spend extra movement to climb.
"""

fly_docstring: str = """ A monster that has a flying speed can use all or part of its movement to fly. Some monsters have the ability to hover, which makes them hard to knock out of the air (as explained in the rules on flying in the Player’s Handbook). Such a monster stops hovering when it falls unconscious.
"""

swim_docstring: str = """ A monster that has a swimming speed doesn’t need to spend extra movement to swim. """


saving_throws_docstring: str = """The Saving Throws entry is reserved for creatures that are adept at resisting certain kinds of effects. For example, a creature that isn’t easily charmed or frightened might gain a bonus on its Wisdom saving throws. Most creatures don’t have special saving throw bonuses, in which case this section is absent.

A saving throw bonus is the sum of a monster’s relevant ability modifier and its proficiency bonus, which is determined by the monster’s challenge rating (as shown in the Proficiency Bonus by Challenge Rating table).

### Table: Proficiency Bonus by Challenge Rating
| Challenge Rating | Proficiency Bonus |
|------------------|-------------------|
| 0                | +2                |
| 1/8              | +2                |
| 1/4              | +2                |
| 1/2              | +2                |
| 1                | +2                |
| 2                | +2                |
| 3                | +2                |
| 4                | +2                |
| 5                | +3                |
| 6                | +3                |
| 7                | +3                |
| 8                | +3                |
| 9                | +4                |
| 10               | +4                |
| 11               | +4                |
| 12               | +4                |
| 13               | +5                |
| 14               | +5                |
| 15               | +5                |
| 16               | +5                |
| 17               | +6                |
| 18               | +6                |
| 19               | +6                |
| 20               | +6                |
| 21               | +7                |
| 22               | +7                |
| 23               | +7                |
| 24               | +7                |
| 25               | +8                |
| 26               | +8                |
| 27               | +8                |
| 28               | +8                |
| 29               | +9                |
| 30               | +9                |
"""

skills_docstring: str = """The Skills entry is reserved for monsters that are proficient in one or more skills. For example, a monster that is very perceptive and stealthy might have bonuses to Wisdom (Perception) and Dexterity (Stealth) checks.

A skill bonus is the sum of a monster’s relevant ability modifier and its proficiency bonus, which is determined by the monster’s challenge rating (as shown in the Proficiency Bonus by Challenge Rating table). Other modifiers might apply. For instance, a monster might have a larger-than-expected bonus (usually double its proficiency bonus) to account for its heightened expertise.
"""

vulnerabilities_resistances_immunities_docstring: str = """Some creatures have vulnerability, resistance, or immunity to certain types of damage. Particular creatures are even resistant or immune to damage from nonmagical attacks (a magical attack is an attack delivered by a spell, a magic item, or another magical source). In addition, some creatures are immune to certain conditions.
"""

armor_weapon_tool_proficiencies_docstring: str = """Assume that a creature is proficient with its armor, weapons, and tools. If you swap them out, you decide whether the creature is proficient with its new equipment.

For example, a hill giant typically wears hide armor and wields a greatclub. You could equip a hill giant with chain mail and a greataxe instead, and assume the giant is proficient with both, one or the other, or neither.
"""

senses_docstring: str = """The Senses entry notes a monster’s passive Wisdom (Perception) score, as well as any special senses the monster might have. Special senses are described below.

- **Blindsight**: A monster with blindsight can perceive its surroundings without relying on sight, within a specific radius. Creatures without eyes, such as grimlocks and gray oozes, typically have this special sense, as do creatures with echolocation or heightened senses, such as bats and true dragons. If a monster is naturally blind, it has a parenthetical note to this effect, indicating that the radius of its blindsight defines the maximum range of its perception.
- **Darkvision**: A monster with darkvision can see in the dark within a specific radius. The monster can see in dim light within the radius as if it were bright light, and in darkness as if it were dim light. The monster can’t discern color in darkness, only shades of gray. Many creatures that live underground have this special sense.
- **Tremorsense**: A monster with tremorsense can detect and pinpoint the origin of vibrations within a specific radius, provided that the monster and the source of the vibrations are in contact with the same ground or substance. Tremorsense can’t be used to detect flying or incorporeal creatures. Many burrowing creatures, such as ankhegs and umber hulks, have this special sense.
- **Truesight**: A monster with truesight can, out to a specific range, see in normal and magical darkness, see invisible creatures and objects, automatically detect visual illusions and succeed on saving throws against them, and perceive the original form of a shapechanger or a creature that is transformed by magic. Furthermore, the monster can see into the Ethereal Plane within the same range.
"""

languages_docstring: str = """The languages that a monster can speak are listed in alphabetical order. Sometimes a monster can understand a language but can’t speak it, and this is noted in its entry. A “—” indicates that a creature neither speaks nor understands any language.
"""

telepathy_docstring: str = """Telepathy is a magical ability that allows a monster to communicate mentally with another creature within a specified range. The contacted creature doesn’t need to share a language with the monster to communicate in this way with it, but it must be able to understand at least one language. A creature without telepathy can receive and respond to telepathic messages but can’t initiate or terminate a telepathic conversation.

A telepathic monster doesn’t need to see a contacted creature and can end the telepathic contact at any time. The contact is broken as soon as the two creatures are no longer within range of each other or if the telepathic monster contacts a different creature within range. A telepathic monster can initiate or terminate a telepathic conversation without using an action, but while the monster is incapacitated, it can’t initiate telepathic contact, and any current contact is terminated.

A creature within the area of an antimagic field or in any other location where magic doesn’t function can’t send or receive telepathic messages.
"""

challenge_docstring: str = """A monster’s challenge rating tells you how great a threat the monster is. An appropriately equipped and well-rested party of four adventurers should be able to defeat a monster that has a challenge rating equal to its level without suffering any deaths. For example, a party of four 3rd-level characters should find a monster with a challenge rating of 3 to be a worthy challenge, but not a deadly one.

Monsters that are significantly weaker than 1st-level characters have a challenge rating lower than 1. Monsters with a challenge rating of 0 are insignificant except in large numbers; those with no effective attacks are worth no experience points, while those that have attacks are worth 10 XP each.

Some monsters present a greater challenge than even a typical 20th-level party can handle. These monsters have a challenge rating of 21 or higher and are specifically designed to test player skill.
"""

experience_points_docstring: str = """The number of experience points (XP) a monster is worth is based on its challenge rating. Typically, XP is awarded for defeating the monster, although the GM may also award XP for neutralizing the threat posed by the monster in some other manner.

Unless something tells you otherwise, a monster summoned by a spell or other magical ability is worth the XP noted in its stat block.

### Table: Experience Points by Challenge Rating
| Challenge Rating | XP      |
|------------------|---------|
| 0                | 0 or 10 |
| 1/8              | 25      |
| 1/4              | 50      |
| 1/2              | 100     |
| 1                | 200     |
| 2                | 450     |
| 3                | 700     |
| 4                | 1,100   |
| 5                | 1,800   |
| 6                | 2,300   |
| 7                | 2,900   |
| 8                | 3,900   |
| 9                | 5,000   |
| 10               | 5,900   |
| 11               | 7,200   |
| 12               | 8,400   |
| 13               | 10,000  |
| 14               | 11,500  |
| 15               | 13,000  |
| 16               | 15,000  |
| 17               | 18,000  |
| 18               | 20,000  |
| 19               | 22,000  |
| 20               | 25,000  |
| 21               | 33,000  |
| 22               | 41,000  |
| 23               | 50,000  |
| 24               | 62,000  |
| 25               | 75,000  |
| 26               | 90,000  |
| 27               | 105,000 |
| 28               | 120,000 |
| 29               | 135,000 |
| 30               | 155,000 |
"""
special_traits_docstring: str = """Special traits (which appear after a monster’s challenge rating but before any actions or reactions) are characteristics that are likely to be relevant in a combat encounter and that require some explanation.

- **Innate Spellcasting**: A monster with the innate ability to cast spells has the Innate Spellcasting special trait. Unless noted otherwise, an innate spell of 1st level or higher is always cast at its lowest possible level and can’t be cast at a higher level. If a monster has a cantrip where its level matters and no level is given, use the monster’s challenge rating.
- **Spellcasting**: A monster with the Spellcasting special trait has a spellcaster level and spell slots, which it uses to cast its spells of 1st level and higher. The spellcaster level is also used for any cantrips included in the feature. The monster has a list of spells known or prepared from a specific class. The list might also include spells from a feature in that class, such as the Divine Domain feature of the cleric or the Druid Circle feature of the druid. The monster is considered a member of that class when attuning to or using a magic item that requires membership in the class or access to its spell list.
- **Psionics**: A monster that casts spells using only the power of its mind has the psionics tag added to its Spellcasting or Innate Spellcasting special trait. This tag carries no special rules of its own, but other parts of the game might refer to it. A monster that has this tag typically doesn’t require any components to cast its spells.
"""

actions_docstring: str = """When a monster takes its action, it can choose from the options in the Actions section of its stat block or use one of the actions available to all creatures, such as the Dash or Hide action.

- **Melee and Ranged Attacks**: The most common actions that a monster will take in combat are melee and ranged attacks. These can be spell attacks or weapon attacks, where the “weapon” might be a manufactured item or a natural weapon, such as a claw or tail spike.
- **Creature vs. Target**: The target of a melee or ranged attack is usually either one creature or one target, the difference being that a “target” can be a creature or an object.
- **Hit**: Any damage dealt or other effects that occur as a result of an attack hitting a target are described after the “Hit” notation. You have the option of taking average damage or rolling the damage; for this reason, both the average damage and the die expression are presented.
- **Miss**: If an attack has an effect that occurs on a miss, that information is presented after the “Miss:” notation.
- **Multiattack**: A creature that can make multiple attacks on its turn has the Multiattack action. A creature can’t use Multiattack when making an opportunity attack, which must be a single melee attack.
- **Ammunition**: A monster carries enough ammunition to make its ranged attacks. You can assume that a monster has 2d4 pieces of ammunition for a thrown weapon attack, and 2d10 pieces of ammunition for a projectile weapon such as a bow or crossbow.
"""

reactions_docstring: str = """If a monster can do something special with its reaction, that information is contained here. If a creature has no special reaction, this section is absent.
"""

limited_usage_docstring: str = """Some special abilities have restrictions on the number of times they can be used.

- **X/Day**: The notation “X/Day” means a special ability can be used X number of times and that a monster must finish a long rest to regain expended uses. For example, “1/Day” means a special ability can be used once and that the monster must finish a long rest to use it again.
- **Recharge X–Y**: The notation “Recharge X–Y” means a monster can use a special ability once and that the ability then has a random chance of recharging during each subsequent round of combat. At the start of each of the monster’s turns, roll a d6. If the roll is one of the numbers in the recharge notation, the monster regains the use of the special ability. The ability also recharges when the monster finishes a short or long rest. For example, “Recharge 5–6” means a monster can use the special ability once. Then, at the start of the monster’s turn, it regains the use of that ability if it rolls a 5 or 6 on a d6.
- **Recharge after a Short or Long Rest**: This notation means that a monster can use a special ability once and then must finish a short or long rest to use it again.
"""

grapple_rules_docstring: str = """Many monsters have special attacks that allow them to quickly grapple prey. When a monster hits with such an attack, it doesn’t need to make an additional ability check to determine whether the grapple succeeds, unless the attack says otherwise.

A creature grappled by the monster can use its action to try to escape. To do so, it must succeed on a Strength (Athletics) or Dexterity (Acrobatics) check against the escape DC in the monster’s stat block. If no escape DC is given, assume the DC is 10 + the monster’s Strength (Athletics) modifier.
"""

equipment_docstring: str = """A stat block rarely refers to equipment, other than armor or weapons used by a monster. A creature that customarily wears clothes, such as a humanoid, is assumed to be dressed appropriately.

You can equip monsters with additional gear and trinkets however you like, and you decide how much of a monster’s equipment is recoverable after the creature is slain and whether any of that equipment is still usable. A battered suit of armor made for a monster is rarely usable by someone else, for instance.

If a spellcasting monster needs material components to cast its spells, assume that it has the material components it needs to cast the spells in its stat block.
"""

legendary_creatures_docstring: str = """A legendary creature can do things that ordinary creatures can’t. It can take special actions outside its turn, and it might exert magical influence for miles around.

If a creature assumes the form of a legendary creature, such as through a spell, it doesn’t gain that form’s legendary actions, lair actions, or regional effects.
"""

legendary_actions_docstring: str = """A legendary creature can take a certain number of special actions—called legendary actions—outside its turn. Only one legendary action option can be used at a time and only at the end of another creature’s turn. A creature regains its spent legendary actions at the start of its turn. It can forgo using them, and it can’t use them while incapacitated or otherwise unable to take actions. If surprised, it can’t use them until after its first turn in the combat.
"""

legendary_lair_docstring: str = """A legendary creature might have a section describing its lair and the special effects it can create while there, either by act of will or simply by being present. Such a section applies only to a legendary creature that spends a great deal of time in its lair.

- **Lair Actions**: If a legendary creature has lair actions, it can use them to harness the ambient magic in its lair. On initiative count 20 (losing all initiative ties), it can use one of its lair action options. It can’t do so while incapacitated or otherwise unable to take actions. If surprised, it can’t use one until after its first turn in the combat.
- **Regional Effects**: The mere presence of a legendary creature can have strange and wondrous effects on its environment, as noted in this section. Regional effects end abruptly or dissipate over time when the legendary creature dies.
"""

npc_customizing_docstring: str = """There are many easy ways to customize the NPCs.

- **Racial Traits**: You can add racial traits to an NPC. For example, a halfling druid might have a speed of 25 feet and the Lucky trait. Adding racial traits to an NPC doesn’t alter its challenge rating.
- **Armor and Weapon Swaps**: You can upgrade or downgrade an NPC’s armor, or add or switch weapons. Adjustments to Armor Class and damage can change an NPC’s challenge rating.
- **Spell Swaps**: One way to customize an NPC spellcaster is to replace one or more of its spells. You can substitute any spell on the NPC’s spell list with a different spell of the same level from the same spell list. Swapping spells in this manner doesn’t alter an NPC’s challenge rating.
- **Magic Items**: The more powerful an NPC, the more likely it has one or more magic items in its possession. An archmage, for example, might have a magic staff or wand, as well as one or more potions and scrolls. Giving an NPC a potent damage-dealing magic item could alter its challenge rating.
"""

creature_traits_docstring: str = """You can create a themed version of an existing creature by giving it one or more of the following traits or actions:

- **Crackling**: This creature crackles with electricity. If you attempt a melee attack against it, you must succeed on a Constitution saving throw or take 1d8 lightning damage. The DC equals 10 + the creature’s highest ability modifier.
- **Soaked**: This creature is immune to fire damage. It magically creates enough drinking water for five creatures (including itself) each day.
- **Whirling**: Whenever this creature makes an attack, it can move its speed.
- **Arcane Armor**: Increase the AC of this creature by 2 and its CR by 1. When this creature takes damage from an attack, it can use its reaction to gain resistance to the triggering damage type until the end of its next turn.
- **Ensorcelled**: Weapon attacks made by this creature do force damage. Melee weapons (including natural weapons like fists, teeth, and claws) emit dim light to a range of 10 feet. The light is a color of your choosing.
- **Mage’s Mobility**: The creature learns one cantrip that requires a spell attack, and whenever it takes the Disengage action, it can choose to cast it. Its attack bonus equals its highest ability modifier + its proficiency bonus.
- **Doom’s Herald**: Once per turn, when the creature hits with a weapon attack, you must succeed on a Charisma saving throw or gain 1 doom point. The DC equals 10 + the creature’s proficiency bonus. A creature possessing doom points reduces its saving throw rolls (including death saving throws) by its current number of doom points. Spells like remove curse and greater restoration can reduce a creature’s accumulated doom points by one. Otherwise, all doom points disappear when the creature completes a long rest.
- **Hate Sense**: This creature knows the location of all creatures within 60 feet of it that aren’t constructs or undead.
- **Visions of the End**: The creature conjures visions of death to horrify its enemies as an action. Any creature within 60 feet that it can see must succeed on a Wisdom saving throw or become frightened of it for 1 minute. The DC equals 10 + the creature’s proficiency bonus. A frightened target can repeat the saving throw at the end of each of its turns, ending the effect on itself on a success.
- **Incorporeal Movement**: The creature can move through other creatures and objects. It takes 5 (1d10) force damage if it ends its turn inside an object.
- **Invisibility**: As an action, the creature magically turns invisible until it chooses to end the effect. The invisibility ends early if the creature attacks or casts a spell. Any equipment the creature wears or carries is also invisible.
- **Waking Dream**: The creature is immune to any effects that would put it to sleep or cause it to become unconscious.
- **Beast Friend (1/Day)**: As an action, the creature summons four beasts of CR 2 or lower that appear in unoccupied spaces within 60 feet of it. The beasts act on their own initiative, but they obey all commands issued to them by the creature (no action required). Each beast disappears when it drops to 0 hit points.
- **Pixie Dust**: The creature gains a flying speed of 30 feet. If it already has a flying speed, it increases by 30 feet.
- **Unseelie Blessing**: The creature has advantage on saving throws against being charmed, and magic can’t put it to sleep.
- **Wild Heart**: At the beginning of each of the creature’s turns, it can use a bonus action to roll a d20. If it rolls lower than its Constitution ability score, it regains hit points equal to its Constitution modifier.
- **Eye-Watering Aroma**: Whenever you begin or end your turn within 10 feet of this creature, you must succeed on a Constitution saving throw or become blinded as your eyes fill with stinging tears. The DC equals 10 + the creature’s proficiency bonus. The condition ends as soon as you move at least 10 feet away from the creature. Targets with more than two eyes have disadvantage on the saving throw.
- **Rending Thorns**: Whenever this creature succeeds on a melee attack by rolling a 19 or 20, your AC is reduced by 1, in addition to suffering the normal effects of the attack. This reduction to AC ends after you take a short or long rest.
- **Wreath of Briars**: When you hit this creature with a melee attack, it can use its reaction to force you to make a Dexterity saving throw, taking 2d8 piercing damage and dropping whatever you are currently holding on a failed save or half as much damage on a successful one. The DC equals 10 + the creature’s proficiency bonus.
- **Plague Form**: The creature has resistance to necrotic damage and immunity to poison damage.
- **Putrid**: Whenever the creature takes bludgeoning, piercing, or slashing damage, all creatures within 5 feet of it take 1d6 poison damage.
- **Toxic Strike**: If the creature hits with a melee attack, the target must succeed on a Constitution saving throw or be poisoned for 1 minute. If the target fails the save by 5 or more, the target is also paralyzed while poisoned in this way. The DC equals 10 + the creature’s proficiency bonus.
- **Half There**: This creature is literally halfway between this plane of existence and another. Attacks against it have disadvantage. Successfully grappling the creature brings it fully into this plane for the duration, removing any benefit to the creature from this feature.
- **Infuriating Redirection**: Once per round, as a reaction to being targeted by a ranged attack, the creature can open a portal to redirect the attack to another creature within 30 feet.
- **Pop Out**: At the end of this creature’s turn, if it did not move, it can teleport to any unoccupied space within 20 feet.
- **Evaporating Aura**: Whenever you enter an area within 20 feet of this creature for the first time in a turn, or start your turn there, any water, wine, spirits, or other nonmagical fluids you carry evaporate and disappear.
- **Hot as Hells**: Whenever you enter an area within 5 feet of this creature for the first time in a turn, or start your turn there, you must succeed on a Constitution saving throw or take fire damage equal to 1d6 + the creature’s proficiency bonus. The DC equals 10 + the creature’s proficiency bonus.
- **Singeing Blow**: Whenever this creature hits with a melee attack, it deals extra fire damage equal to its proficiency bonus.
- **Ritualist**: This creature knows three ritual spells of your choice. These spells can be from any spell list, but they can’t be of a level that exceeds this creature’s proficiency bonus. The creature can cast each of these spells once per long rest without expending material components. If a ritual requires a saving throw, the DC equals 10 + this creature’s proficiency bonus.
- **Superior Focus**: This creature has advantage on Constitution saving throws to maintain concentration.
- **Blessing of Vitality**: The creature regenerates 10 hit points at the start of its turn. If the creature takes necrotic damage, this trait doesn’t function at the start of the creature’s next turn. The creature dies only if it starts its turn with 0 hit points and doesn’t regenerate.
- **Divine Protection**: If you target the creature with an attack or a harmful spell, you must first make a Wisdom saving throw (DC equals 10 + this creature’s proficiency bonus). On a success, you attack as normal, and you are immune to this feature for 1 minute. On a failed save, you must choose a new target or lose the attack or spell. If the creature attacks another creature, that target is immune to this feature for 1 minute.
- **Heavenly Wrath**: Whenever this creature makes a successful weapon attack, they deal an additional 1d8 radiant damage.
- **Dancing Shadows**: While standing in dim light or darkness, the creature can use their bonus action to teleport to a different unoccupied space of dim light or darkness it can see within 30 feet.
- **Shadow Cloak**: Whenever the creature takes damage, it can use its reaction to create a 10-foot-radius sphere of magical darkness centered on itself. The darkness remains until dispelled or until the beginning of the creature’s next turn. The creature can use this feature a number of times equal to its proficiency bonus.
- **Shadow Sight**: The creature has darkvision out to a range of 60 feet (if they don’t already have darkvision) and can see in magical darkness out to the same distance.
- **Ephemeral**: The creature is not completely grounded in material space, and attacks against it have disadvantage. If the creature is hit by an attack, this trait is disrupted until the end of its next turn.
- **Incorporeal**: This creature can move through other creatures and objects as if they were difficult terrain. It takes 5 (1d10) force damage if it ends its turn inside an object.
- **Shapeless**: This creature is invisible except to creatures with truesight or under the effects of spells like detect magic or see invisibility.
- **Enhanced Spellcasting**: Any spells this creature casts have their saving throw DC increased by 1.
- **Potent Spellcasting (CR 10 or Higher Creature Only)**: Creatures have disadvantage on saving throws made to resist spells cast by this creature.
"""



---

## equipment

from typing import List, Optional, Callable, TYPE_CHECKING
from pydantic import BaseModel, Field
from enum import Enum

from infinipy.dnd.core import  AbilityScores,  Damage, Range,  DirectionalContextualModifier


if TYPE_CHECKING:
    from infinipy.dnd.statsblock import AttackType
    from infinipy.dnd.statsblock import StatsBlock
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
    attack_type: "AttackType"
    properties: List[WeaponProperty]
    range: Range

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

    def compute_ac(self, attacker: Optional['StatsBlock'] = None) -> int:
        total_ac = self.base_ac
        if attacker:
            total_ac += self.contextual_modifiers.compute_self_bonus(attacker, self)
            total_ac -= self.contextual_modifiers.compute_opponent_bonus(attacker, self)
        return total_ac

    def give_advantage(self, attacker: 'StatsBlock') -> bool:
        return self.contextual_modifiers.gives_opponent_advantage(attacker, self)

    def give_disadvantage(self, attacker: 'StatsBlock') -> bool:
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

---

## init



---

## goblin

from infinipy.dnd.statsblock import StatsBlock
from infinipy.dnd.equipment import Armor, ArmorType, Shield, Weapon, WeaponProperty, ArmorClass
from infinipy.dnd.actions import Action, ActionCost, ActionType, Targeting, TargetType, AttackType, Attack
from infinipy.dnd.core import Ability, AbilityScores, AbilityScore, ModifiableValue, Dice, \
 Damage, DamageType, Range, RangeType, Size, MonsterType, Alignment, Speed, Skills, Sense, SensesType, Language, ActionEconomy, SkillBonus

class GoblinNimbleEscape(Action):
    def __init__(self, **data):
        super().__init__(
            name="Nimble Escape",
            description="The goblin can take the Disengage or Hide action as a bonus action on each of its turns.",
            cost=[ActionCost(type=ActionType.BONUS_ACTION, cost=1)],
            limited_usage=None,
            targeting=Targeting(type=TargetType.SELF),
            **data
        )

def create_goblin() -> StatsBlock:
    goblin = StatsBlock(
        name="Goblin",
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
        armor_class=ArmorClass(base_ac=15),  # Will be recalculated after equipping armor and shield
        challenge=0.25,
        experience_points=50,
        skills=[SkillBonus(skill=Skills.STEALTH, bonus=6)],
        senses=[Sense(type=SensesType.DARKVISION, range=60)],
        languages=[Language.COMMON, Language.GOBLIN],
        special_traits=["Nimble Escape: The goblin can take the Disengage or Hide action as a bonus action on each of its turns."],
        hit_dice=Dice(dice_count=2, dice_value=6, modifier=0),
        action_economy=ActionEconomy(speed=30)
    )

    # Equip armor and shield
    leather_armor = Armor(name="Leather Armor", type=ArmorType.LIGHT, base_ac=11, dex_bonus=True)
    goblin.equip_armor(leather_armor)
    shield = Shield(name="Shield", ac_bonus=2)
    goblin.equip_shield(shield)

    # Add weapons
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

    # Add Nimble Escape action
    goblin.add_action(GoblinNimbleEscape(stats_block=goblin))

    return goblin

def print_goblin_details(goblin: StatsBlock):
    print("\nGoblin Details:")
    print(f"Name: {goblin.name}")
    print(f"Size: {goblin.size.value}")
    print(f"Type: {goblin.type.value}")
    print(f"Alignment: {goblin.alignment.value}")
    print("Ability Scores:")
    for ability in Ability:
        score = getattr(goblin.ability_scores, ability.value.lower())
        print(f"  {ability.value}: {score.score.total_value} (Modifier: {score.modifier})")
    print(f"Speed: Walk {goblin.speed.walk.get_value()} ft")
    print(f"Armor Class: {goblin.armor_class.compute_ac()}")
    print(f"Hit Points: {goblin.current_hit_points}/{goblin.max_hit_points}")
    print(f"Proficiency Bonus: +{goblin.proficiency_bonus}")
    print("Skills:")
    for skill in goblin.skills:
        print(f"  {skill.skill.value}: +{skill.bonus}")
    print("Senses:")
    for sense in goblin.senses:
        print(f"  {sense.type.value}: {sense.range} ft")
    print(f"Languages: {', '.join([lang.value for lang in goblin.languages])}")
    print(f"Challenge Rating: {goblin.challenge} ({goblin.experience_points} XP)")
    print("Special Traits:")
    for trait in goblin.special_traits:
        print(f"  {trait}")
    print("Actions:")
    for action in goblin.actions:
        if isinstance(action, Attack):
            print(f"  {action.action_docstring()}")
        else:
            print(f"  {action.name}: {action.description}")
    print(f"Equipment: {', '.join([weapon.name for weapon in goblin.weapons])}, "
          f"{goblin.armor_class.equipped_armor.name if goblin.armor_class.equipped_armor else 'No Armor'}, "
          f"{goblin.armor_class.equipped_shield.name if goblin.armor_class.equipped_shield else 'No Shield'}")

def main():
    goblin = create_goblin()
    print_goblin_details(goblin)

if __name__ == "__main__":
    main()

---

## skeleton

from infinipy.dnd.statsblock import StatsBlock
from infinipy.dnd.equipment import Armor, ArmorType, Shield, Weapon, WeaponProperty, ArmorClass
from infinipy.dnd.actions import Action, ActionCost, ActionType, Targeting, TargetType, AttackType, Attack
from infinipy.dnd.core import Ability, AbilityScores, AbilityScore, ModifiableValue, Dice, \
 Damage, DamageType, Range, RangeType, Size, MonsterType, Alignment, Speed, Skills, Sense, SensesType, Language, ActionEconomy, SkillBonus
from typing import List
import random

def create_skeleton() -> StatsBlock:
    skeleton = StatsBlock(
        name="Skeleton",
        size=Size.MEDIUM,
        type=MonsterType.UNDEAD,
        alignment=Alignment.LAWFUL_EVIL,
        ability_scores=AbilityScores(
            strength=AbilityScore(ability=Ability.STR, score=ModifiableValue(base_value=10)),
            dexterity=AbilityScore(ability=Ability.DEX, score=ModifiableValue(base_value=14)),
            constitution=AbilityScore(ability=Ability.CON, score=ModifiableValue(base_value=15)),
            intelligence=AbilityScore(ability=Ability.INT, score=ModifiableValue(base_value=6)),
            wisdom=AbilityScore(ability=Ability.WIS, score=ModifiableValue(base_value=8)),
            charisma=AbilityScore(ability=Ability.CHA, score=ModifiableValue(base_value=5))
        ),
        speed=Speed(walk=ModifiableValue(base_value=30)),
        armor_class=ArmorClass(base_ac=13),  # Will be recalculated after equipping armor
        vulnerabilities=[DamageType.BLUDGEONING],
        immunities=[DamageType.POISON],
        senses=[Sense(type=SensesType.DARKVISION, range=60)],
        languages=["Common"],
        challenge=0.25,
        experience_points=50,
        special_traits=[
            "Undead Nature: The skeleton doesn't require air, food, drink, or sleep."
        ],
        # current_hit_points=10,
        hit_dice=Dice(dice_count=2, dice_value=8, modifier=0),
        action_economy=ActionEconomy(speed=30)
    )

    # Equip armor
    armor_scraps = Armor(name="Armor Scraps", type=ArmorType.LIGHT, base_ac=13, dex_bonus=True)
    skeleton.equip_armor(armor_scraps)

    # Add weapons
    shortsword = Weapon(
        name="Shortsword",
        damage=Damage(dice=Dice(dice_count=1, dice_value=6, modifier=0), type=DamageType.PIERCING),
        attack_type=AttackType.MELEE_WEAPON,
        properties=[WeaponProperty.FINESSE],
        range=Range(type=RangeType.REACH, normal=5)
    )
    skeleton.add_weapon(shortsword)

    shortbow = Weapon(
        name="Shortbow",
        damage=Damage(dice=Dice(dice_count=1, dice_value=6, modifier=0), type=DamageType.PIERCING),
        attack_type=AttackType.RANGED_WEAPON,
        properties=[WeaponProperty.RANGED],
        range=Range(type=RangeType.RANGE, normal=80, long=320)
    )
    skeleton.add_weapon(shortbow)

    # Add Undead Fortitude trait
    skeleton.add_action(UndeadFortitude(stats_block=skeleton))

    return skeleton

class UndeadFortitude(Action):
    def __init__(self, stats_block: 'StatsBlock'):
        super().__init__(
            name="Undead Fortitude",
            description="If damage reduces the skeleton to 0 hit points, it must make a Constitution saving throw with a DC of 5 + the damage taken, unless the damage is radiant or from a critical hit. On a success, the skeleton drops to 1 hit point instead.",
            cost=[],  # This is a passive trait, so no action cost
            limited_usage=None,
            targeting=Targeting(type=TargetType.SELF),
            stats_block=stats_block
        )

    def execute(self, damage: int, damage_type: DamageType, is_critical: bool) -> bool:
        if self.stats_block.current_hit_points == 0 and damage_type != DamageType.RADIANT and not is_critical:
            dc = 5 + damage
            con_save = self.stats_block.ability_scores.constitution.modifier + random.randint(1, 20)
            if con_save >= dc:
                self.stats_block.current_hit_points = 1
                return True
        return False

def print_skeleton_details(skeleton: StatsBlock):
    print("\nSkeleton Details:")
    print(f"Name: {skeleton.name}")
    print(f"Size: {skeleton.size.value}")
    print(f"Type: {skeleton.type.value}")
    print(f"Alignment: {skeleton.alignment.value}")
    print("Ability Scores:")
    for ability in Ability:
        score = getattr(skeleton.ability_scores, ability.value.lower())
        print(f"  {ability.value}: {score.score.total_value} (Modifier: {score.modifier})")
    print(f"Speed: Walk {skeleton.speed.walk.get_value()} ft")
    print(f"Armor Class: {skeleton.armor_class.compute_ac()}")
    print(f"Hit Points: {skeleton.current_hit_points}/{skeleton.max_hit_points}")
    print(f"Proficiency Bonus: +{skeleton.proficiency_bonus}")
    print("Damage Vulnerabilities: " + ", ".join([v.value for v in skeleton.vulnerabilities]))
    print("Damage Immunities: " + ", ".join([i.value for i in skeleton.immunities]))
    print("Senses:")
    for sense in skeleton.senses:
        print(f"  {sense.type.value}: {sense.range} ft")
    print(f"Languages: {', '.join([lang.value for lang in skeleton.languages])}")
    print(f"Challenge Rating: {skeleton.challenge} ({skeleton.experience_points} XP)")
    print("Special Traits:")
    for trait in skeleton.special_traits:
        print(f"  {trait}")
    print("Actions:")
    for action in skeleton.actions:
        if isinstance(action, Attack):
            print(f"  {action.action_docstring()}")
        else:
            print(f"  {action.name}: {action.description}")
    print(f"Equipment: {', '.join([weapon.name for weapon in skeleton.weapons])}, "
          f"{skeleton.armor_class.equipped_armor.name if skeleton.armor_class.equipped_armor else 'No Armor'}")

def main():
    skeleton = create_skeleton()
    print_skeleton_details(skeleton)

if __name__ == "__main__":
    main()

---

## statsblock

from typing import List, Dict, Optional, Set, Tuple
from pydantic import BaseModel, Field, computed_field
from infinipy.dnd.docstrings import *
import uuid
from infinipy.dnd.core import Ability, Size, MonsterType, Alignment, AbilityScores, Speed, SavingThrow, SkillBonus, DamageType, \
    Sense, Language, Dice, ModifiableValue, Skills, Targeting, ActionEconomy, ActionCost, ActionType, TargetRequirementType, TargetType \
    
from infinipy.dnd.conditions import Condition
from infinipy.dnd.actions import Action, Attack,Dash, Disengage, Dodge, Help, Hide, AttackType
from infinipy.dnd.equipment import Armor, Shield, Weapon, ArmorClass, WeaponProperty

from infinipy.dnd.actions import Dodge, Disengage, Dash, Hide, Help, Attack

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

#fully initalize the models that were using the StatsBlock class as a forward reference
Dodge.model_rebuild()
Disengage.model_rebuild()
Dash.model_rebuild()
Hide.model_rebuild()
Help.model_rebuild()
Attack.model_rebuild()


---

## blinded

from infinipy.dnd.statsblock import *
from infinipy.dnd.monsters.goblin import create_goblin
from infinipy.dnd.monsters.skeleton import create_skeleton
from infinipy.dnd.conditions import Blinded, Duration, DurationType

def print_goblin_details(goblin):
    print(f"Goblin Details:\nName: {goblin.name}\nSpeed: {goblin.speed.walk.get_value()} ft\nArmor Class: {goblin.armor_class.compute_base_ac(goblin.ability_scores)}")
    print(f"Hit Points: {goblin.current_hit_points}/{goblin.max_hit_points}\nProficiency Bonus: +{goblin.proficiency_bonus}")

def print_skeleton_details(skeleton):
    print(f"Skeleton Details:\nName: {skeleton.name}\nSpeed: {skeleton.speed.walk.get_value()} ft\nArmor Class: {skeleton.armor_class.compute_base_ac(skeleton.ability_scores)}")
    print(f"Hit Points: {skeleton.current_hit_points}/{skeleton.max_hit_points}\nProficiency Bonus: +{skeleton.proficiency_bonus}")

def test_blinded_condition():
    goblin = create_goblin()
    skeleton = create_skeleton()
    
    print("\n--- Initial State ---")
    print_goblin_details(goblin)
    print("\nSkeleton:")
    print_skeleton_details(skeleton)
    
    print("\n--- Goblin attacks Skeleton (no conditions) ---")
    attack_action = next(action for action in goblin.actions if isinstance(action, Attack))
    hit, details = attack_action.roll_to_hit(skeleton, verbose=True)
    print(f"Advantage status: {details['advantage_status']}")
    print(f"Attack roll: {details['roll']}, Total modifiers: {details['self_bonus'] - details['opponent_bonus']}")
    print(details)
    if hit:
        damage = attack_action.roll_damage()
        skeleton.take_damage(damage)
        print(f"Goblin hits Skeleton for {damage} damage. Skeleton HP: {skeleton.current_hit_points}")
    else:
        print(f"Goblin misses the attack. Required AC: {details['armor_class']}, Roll: {details['roll']}")
    
    # Apply the Blinded condition to the goblin
    blinded_condition = Blinded(name="Blinded", duration=Duration(time=1, type=DurationType.ROUNDS))
    goblin.apply_condition(blinded_condition)
    
    print("\n--- State After Applying Blinded Condition ---")
    print_goblin_details(goblin)
    
    print("\n--- Goblin attacks Skeleton (Blinded condition) ---")
    attack_action = next(action for action in goblin.actions if isinstance(action, Attack))
    hit, details = attack_action.roll_to_hit(skeleton, verbose=True)
    print(f"Advantage status: {details['advantage_status']}")
    print(f"Attack roll: {details['roll']}, Total modifiers: {details['self_bonus'] - details['opponent_bonus']}")
    print(details)
    if hit:
        damage = attack_action.roll_damage()
        skeleton.take_damage(damage)
        print(f"Goblin hits Skeleton for {damage} damage. Skeleton HP: {skeleton.current_hit_points}")
    else:
        print(f"Goblin misses the attack due to being blinded. Required AC: {details['armor_class']}, Roll: {details['roll']}")
    
    print("\n--- Advancing Rounds ---")
    goblin.update_conditions()
    
    print("\n--- State After Advancing Rounds ---")
    print_goblin_details(goblin)
    
    goblin.update_conditions()
    
    print("\n--- State After Another Round ---")
    print_goblin_details(goblin)

def main():
    test_blinded_condition()

if __name__ == "__main__":
    main()


---

