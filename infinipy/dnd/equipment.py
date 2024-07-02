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