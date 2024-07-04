from pydantic import BaseModel, Field, computed_field

from typing import List, Optional, Union, Dict, Any, Tuple, Set, Callable, TYPE_CHECKING
from enum import Enum
from infinipy.dnd.contextual import ModifiableValue, AdvantageStatus
from infinipy.dnd.core import  Dice, Ability, DamageType, Damage, Range, RangeType, ShapeType, TargetType, TargetRequirementType, StatusEffect, Duration, LimitedUsage, UsageType, RechargeType, ActionType, ActionCost, Targeting, AdvantageTracker
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
    contextual_conditions: Dict[str, Callable[[Dict[str, Any]], Tuple[bool, str]]] = Field(default_factory=dict)

    def prerequisite(self, stats_block: 'StatsBlock', target:'StatsBlock') -> Tuple[bool, str]:
        source = stats_block

        for condition_name, condition_check in self.contextual_conditions.items():
            can_perform, reason = condition_check(source,target)
            if not can_perform:
                return False, reason
        return True, ""
    
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
    blocked_targets: Set[str] = Field(default_factory=set)
    is_critical_hit: bool = False
    hit_bonus: ModifiableValue = Field(default_factory=lambda: ModifiableValue(base_value=0))

    def __init__(self, **data):
        super().__init__(**data)
        self.update_hit_bonus()

    def update_hit_bonus(self):
        ability_modifier = getattr(self.stats_block.ability_scores, self.ability.value.lower()).get_modifier(self.stats_block)
        self.hit_bonus.base_value = ability_modifier + self.stats_block.proficiency_bonus

    @computed_field
    def average_damage(self) -> float:
        ability_modifier = getattr(self.stats_block.ability_scores, self.ability.value.lower()).get_modifier(self.stats_block)
        return sum(d.dice.expected_value() + ability_modifier for d in self.damage)

    def action_docstring(self):
        attack_range = str(self.range)
        ability_modifier = getattr(self.stats_block.ability_scores, self.ability.value.lower()).get_modifier(self.stats_block)
        damage_strings = [
            f"{d.dice.dice_count}d{d.dice.dice_value} + {ability_modifier} {d.type.value} damage"
            for d in self.damage
        ]
        damage_string = " plus ".join(damage_strings)
        return f"{self.attack_type.value} Attack: +{self.hit_bonus.get_value(self.stats_block)} to hit, {attack_range}, {self.targeting.target_docstring()}. Hit: {damage_string}. Average damage: {self.average_damage:.1f}."

    # ... rest of the class remains the same
    def add_contextual_advantage(self, source: str, condition: Callable[['StatsBlock', 'StatsBlock'], bool]):
        self.hit_bonus.self_effects.add_advantage_condition(source, condition)

    def add_contextual_disadvantage(self, source: str, condition: Callable[['StatsBlock', 'StatsBlock'], bool]):
        self.hit_bonus.self_effects.add_disadvantage_condition(source, condition)

    def add_contextual_bonus(self, source: str, bonus: Callable[['StatsBlock', 'StatsBlock'], int]):
        self.hit_bonus.self_effects.add_bonus(source, bonus)

    def roll_to_hit(self, target: 'StatsBlock', verbose: bool = False) -> Union[bool, Tuple[bool, Dict[str, Any]]]:
        total_hit_bonus = self.hit_bonus.get_value(self.stats_block, target)
    
        advantage_status = AdvantageStatus.NONE
        if self.hit_bonus.self_effects.has_disadvantage(self.stats_block, target):
            advantage_status = AdvantageStatus.DISADVANTAGE
        elif self.hit_bonus.self_effects.has_advantage(self.stats_block, target):
            advantage_status = AdvantageStatus.ADVANTAGE
        
        # Check if the target's armor class gives advantage
        if target.armor_class.gives_attacker_advantage(target, self.stats_block):
            if advantage_status == AdvantageStatus.DISADVANTAGE:
                advantage_status = AdvantageStatus.NONE
            else:
                advantage_status = AdvantageStatus.ADVANTAGE
        
        dice = Dice(dice_count=1, dice_value=20, modifier=total_hit_bonus, advantage_status=advantage_status)
        roll, roll_status = dice.roll_with_advantage()

        self.is_critical_hit = roll_status == "critical_hit"
        hit = roll >= target.armor_class.get_value(target, self.stats_block)

        if verbose:
            details = {
                "hit": hit,
                "roll": roll,
                "roll_status": roll_status,
                "total_hit_bonus": total_hit_bonus,
                "advantage_status": advantage_status,
                "armor_class": target.armor_class.get_value(target, self.stats_block),
                "is_critical_hit": self.is_critical_hit,
                "self_advantages": self.hit_bonus.self_effects.advantage_conditions,
                "self_disadvantages": self.hit_bonus.self_effects.disadvantage_conditions,
                "target_advantages": target.armor_class.base_ac.target_effects.advantage_conditions,
                "target_disadvantages": target.armor_class.base_ac.target_effects.disadvantage_conditions
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
                advantage_status=self.hit_bonus.get_advantage_status(self.stats_block)
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
