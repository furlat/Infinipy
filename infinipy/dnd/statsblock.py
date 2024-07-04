from typing import List, Dict, Optional, Set, Tuple, Any, Union
from pydantic import BaseModel, Field, computed_field
from infinipy.dnd.docstrings import *
import uuid
from infinipy.dnd.contextual import ModifiableValue, ContextualEffects
from infinipy.dnd.core import Ability, SkillSet,Size, MonsterType, Alignment, AbilityScores, Speed, SavingThrow, SkillBonus, DamageType, \
    Sense, Language, Dice, Skills, Targeting, ActionEconomy, ActionCost, ActionType, TargetRequirementType, TargetType
from infinipy.dnd.conditions import Condition
from infinipy.dnd.actions import Action, Attack, Dash, Disengage, Dodge, Help, Hide, AttackType
from infinipy.dnd.equipment import Armor, Shield, Weapon, ArmorClass, WeaponProperty

class StatsBlock(BaseModel):
    name: str = Field(..., description="name of the creature")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="unique identifier for the creature")
    size: Size = Field(..., description=size_docstring)
    type: MonsterType = Field(..., description=type_docstring)
    alignment: Alignment = Field(..., description=alignment_docstring)
    speed: Speed = Field(Speed(walk=ModifiableValue(base_value=30)), description=speed_docstring)
    ability_scores: AbilityScores = Field(default_factory=AbilityScores)
    saving_throws: Dict[Ability, SavingThrow] = Field(default_factory=lambda: {ability: SavingThrow(ability=ability, proficient=False) for ability in Ability})
    skills: SkillSet = Field(default_factory=SkillSet)
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
    armor_class: ArmorClass = Field(default_factory=lambda: ArmorClass(base_ac=ModifiableValue(base_value=10)))
    weapons: List[Weapon] = Field(default_factory=list)
    hit_dice: Dice
    hit_point_bonus: ModifiableValue = Field(default_factory=lambda: ModifiableValue(base_value=0))
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
            print(f"Condition {key}  expired on {self.name}")
            self.remove_condition(key)

    def apply_active_conditions(self):
        for condition in self.active_conditions.values():
            condition.apply(self)

    def _recompute_fields(self):
        self.armor_class.compute_base_ac(self.ability_scores)
        self._compute_passive_perception()
        self.action_economy.movement.base_value = self.speed.walk.get_value(self)
        self.action_economy.reset()
        for action in self.actions:
            if isinstance(action, Attack):
                action.update_hit_bonus()
        self.apply_active_conditions()

    @computed_field
    def max_hit_points(self) -> int:
        con_modifier = self.ability_scores.constitution.get_modifier(self)
        average_hp = (self.hit_dice.expected_value()) + \
                     (con_modifier * self.hit_dice.dice_count) + \
                     self.hit_point_bonus.get_value(self)
        return max(1, int(average_hp))

    def apply_condition(self, condition: Condition):
        if condition.name in self.modifier_immunity:
            return
        key = condition.name
        if key not in self.active_conditions:
            print(f"Applying condition {condition.name} with ID {condition.id} to {self.name}")
            self.active_conditions[key] = condition
            # condition.apply(self)
            self._recompute_fields()

    def remove_condition(self, condition_name: str):
        key = condition_name
        if key in self.active_conditions:
            print(f"Removing condition {condition_name}  from {self.name}")
            condition = self.active_conditions.pop(key)
            condition.remove(self)
            self._recompute_fields()

    def get_conditions_by_name(self, name: str) -> List[Condition]:
        return [cond for key, cond in self.active_conditions.items() if key == name]



    @computed_field
    def armor_class_value(self) -> int:
        return self.armor_class.get_value(self)

    @computed_field
    def proficiency_bonus(self) -> int:
        return self.ability_scores.proficiency_bonus.get_value(self)

    @computed_field
    def initiative(self) -> int:
        return self.ability_scores.dexterity.get_modifier(self)

    @computed_field
    def passive_perception(self) -> int:
        return self.computed_passive_perception.get_value(self)

    def _compute_passive_perception(self):
        perception_skill = self.skills.get_skill(Skills.PERCEPTION)
        self.computed_passive_perception.base_value = 10 + perception_skill.get_bonus(self)

    def perform_ability_check(self, ability: Ability, dc: int, target: Any = None) -> bool:
        return self.ability_scores.get_ability_score(ability).perform_ability_check(self, dc, target)

    def perform_skill_check(self, skill: Skills, dc: int, context: Any = None, return_roll: bool = False) -> Union[bool, Tuple[int, int, int]]:
        skill_obj = self.skills.get_skill(skill)
        roll, total = skill_obj.perform_check(self, dc, context, return_roll=True)
        if return_roll:
            return roll, total, dc
        return total >= dc

    def perform_saving_throw(self, ability: Ability, dc: int, target: Any = None) -> bool:
        return self.saving_throws[ability].perform_save(self, dc, target)

    def set_skill_proficiency(self, skill: Skills):
        self.skills.set_proficiency(skill)

    def set_skill_expertise(self, skill: Skills):
        self.skills.set_expertise(skill)

    def set_saving_throw_proficiency(self, ability: Ability):
        self.saving_throws[ability].proficient = True

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
        self.armor_class.equip_armor(armor, self.ability_scores)
        self._recompute_fields()

    def unequip_armor(self):
        self.armor_class.unequip_armor(self.ability_scores)
        self._recompute_fields()

    def equip_shield(self, shield: Shield):
        self.armor_class.equip_shield(shield, self.ability_scores)
        self._recompute_fields()

    def unequip_shield(self):
        self.armor_class.unequip_shield(self.ability_scores)
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
        self.hit_point_bonus.add_static_modifier("bonus", bonus)
        self._recompute_fields()

    def remove_hit_point_bonus(self, bonus: int):
        self.hit_point_bonus.remove_static_modifier("bonus")
        self._recompute_fields()

ModifiableValue.model_rebuild()
Dodge.model_rebuild()
Disengage.model_rebuild()
Dash.model_rebuild()
Hide.model_rebuild()
Help.model_rebuild()
Attack.model_rebuild()
# ArmorClass.model_rebuild()
# Weapon.model_rebuild()