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