from typing import List, Optional, Callable, TYPE_CHECKING
from pydantic import BaseModel, Field
from enum import Enum
from infinipy.dnd.contextual import ModifiableValue, ContextualEffects

if TYPE_CHECKING:
    from infinipy.dnd.statsblock import StatsBlock
    from infinipy.dnd.core import AbilityScores, Damage, Range
    from infinipy.dnd.actions import AttackType

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
    damage: 'Damage'
    attack_type: 'AttackType'
    properties: List[WeaponProperty]
    range: 'Range'

class ArmorClass(BaseModel):
    base_ac: ModifiableValue = Field(default_factory=lambda: ModifiableValue(base_value=10))
    equipped_armor: Optional[Armor] = None
    equipped_shield: Optional[Shield] = None

    def compute_base_ac(self, ability_scores: 'AbilityScores') -> int:
        base_ac = 10 + ability_scores.dexterity.get_modifier(None)
        if self.equipped_armor:
            base_ac = self.equipped_armor.base_ac
            if self.equipped_armor.dex_bonus:
                dex_bonus = ability_scores.dexterity.get_modifier(None)
                if self.equipped_armor.max_dex_bonus is not None:
                    dex_bonus = min(dex_bonus, self.equipped_armor.max_dex_bonus)
                base_ac += dex_bonus
        if self.equipped_shield:
            base_ac += self.equipped_shield.ac_bonus
        
        self.base_ac.base_value = base_ac
        return self.base_ac.base_value

    def get_value(self, stats_block: 'StatsBlock', attacker: Optional['StatsBlock'] = None) -> int:
        return self.base_ac.get_value(stats_block, attacker)

    def gives_attacker_advantage(self, stats_block: 'StatsBlock', attacker: 'StatsBlock') -> bool:
        return any(cond(attacker, stats_block) for _, cond in self.base_ac.target_effects.advantage_conditions)

    def gives_attacker_disadvantage(self, stats_block: 'StatsBlock', attacker: 'StatsBlock') -> bool:
        return any(cond(attacker, stats_block) for _, cond in self.base_ac.target_effects.disadvantage_conditions)

    def add_self_bonus(self, source: str, bonus: Callable[['StatsBlock', Optional['StatsBlock']], int]):
        self.base_ac.self_effects.add_bonus(source, bonus)

    def add_opponent_bonus(self, source: str, bonus: Callable[['StatsBlock', Optional['StatsBlock']], int]):
        self.base_ac.target_effects.add_bonus(source, bonus)

    def add_self_advantage_condition(self, source: str, condition: Callable[['StatsBlock', Optional['StatsBlock']], bool]):
        self.base_ac.self_effects.add_advantage_condition(source, condition)

    def add_opponent_advantage_condition(self, source: str, condition: Callable[['StatsBlock', Optional['StatsBlock']], bool]):
        self.base_ac.target_effects.add_advantage_condition(source, condition)

    def add_self_disadvantage_condition(self, source: str, condition: Callable[['StatsBlock', Optional['StatsBlock']], bool]):
        self.base_ac.self_effects.add_disadvantage_condition(source, condition)

    def add_opponent_disadvantage_condition(self, source: str, condition: Callable[['StatsBlock', Optional['StatsBlock']], bool]):
        self.base_ac.target_effects.add_disadvantage_condition(source, condition)

    def equip_armor(self, armor: Armor, ability_scores: 'AbilityScores'):
        self.equipped_armor = armor
        self.compute_base_ac(ability_scores)

    def unequip_armor(self, ability_scores: 'AbilityScores'):
        self.equipped_armor = None
        self.compute_base_ac(ability_scores)

    def equip_shield(self, shield: Shield, ability_scores: 'AbilityScores'):
        self.equipped_shield = shield
        self.compute_base_ac(ability_scores)

    def unequip_shield(self, ability_scores: 'AbilityScores'):
        self.equipped_shield = None
        self.compute_base_ac(ability_scores)