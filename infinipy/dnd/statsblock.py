from typing import List, Dict, Optional, Set, Tuple, Any, Union, Callable
from pydantic import BaseModel, Field, computed_field
from infinipy.dnd.docstrings import *
import uuid
from infinipy.dnd.contextual import ModifiableValue, ContextualEffects, ContextAwareCondition
from infinipy.dnd.core import Ability, SkillSet,Size, MonsterType, Alignment, AbilityScores, Speed, SavingThrow,SavingThrows, SkillBonus, DamageType, \
    Sense, Language, Dice, Skills, Targeting, ActionEconomy, ActionCost, ActionType, TargetRequirementType, TargetType
from infinipy.dnd.conditions import Condition
from infinipy.dnd.base_actions import Action, Attack, AttackType,SelfCondition
from infinipy.dnd.actions import Dodge, Dash
from infinipy.dnd.equipment import Armor, Shield, Weapon, ArmorClass, WeaponProperty

class StatsBlock(BaseModel):
    name: str = Field(default="Unnamed", description="name of the creature")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="unique identifier for the creature")
    size: Size = Field(default=Size.MEDIUM, description=size_docstring)
    type: MonsterType = Field(default=MonsterType.HUMANOID, description=type_docstring)
    alignment: Alignment = Field(default=Alignment.TRUE_NEUTRAL, description=alignment_docstring)
    speed: Speed = Field(default_factory=lambda: Speed(walk=ModifiableValue(base_value=30)), description=speed_docstring)
    ability_scores: AbilityScores = Field(default_factory=AbilityScores)
    saving_throws: SavingThrows = Field(default_factory=SavingThrows)
    skills: SkillSet = Field(default_factory=SkillSet)
    vulnerabilities: List[DamageType] = Field(default_factory=list, description=vulnerabilities_resistances_immunities_docstring)
    resistances: List[DamageType] = Field(default_factory=list, description=vulnerabilities_resistances_immunities_docstring)
    immunities: List[DamageType] = Field(default_factory=list, description=vulnerabilities_resistances_immunities_docstring)
    senses: List[Sense] = Field(default_factory=list, description=senses_docstring)
    languages: List[Language] = Field(default_factory=list, description=languages_docstring)
    telepathy: int = Field(default=0, description=telepathy_docstring)
    challenge: float = Field(default=0.0, description=challenge_docstring)
    experience_points: int = Field(default=0, description=experience_points_docstring)
    special_traits: List[str] = Field(default_factory=list, description=special_traits_docstring)
    actions: List[Action] = Field(default_factory=list, description=actions_docstring)
    reactions: List[Action] = Field(default_factory=list, description=reactions_docstring)
    legendary_actions: List[Action] = Field(default_factory=list, description=legendary_actions_docstring)
    lair_actions: List[Action] = Field(default_factory=list, description=legendary_lair_docstring)
    regional_effects: List[str] = Field(default_factory=list, description=legendary_lair_docstring)
    armor_class: ArmorClass = Field(default_factory=lambda: ArmorClass(base_ac=ModifiableValue(base_value=10)))
    weapons: List[Weapon] = Field(default_factory=list)
    hit_dice: Dice = Field(default_factory=lambda: Dice(dice_count=1, dice_value=8, modifier=0))
    hit_point_bonus: ModifiableValue = Field(default_factory=lambda: ModifiableValue(base_value=0))
    current_hit_points: int = Field(default=0)
    computed_passive_perception: ModifiableValue = Field(default_factory=lambda: ModifiableValue(base_value=10))
    action_economy: ActionEconomy = Field(default_factory=lambda: ActionEconomy(speed=30))
    active_conditions: Dict[Tuple[str, str], Condition] = Field(default_factory=dict)
    modifier_immunity: List[str] = Field(default_factory=list)
    line_of_sight: Set[str] = Field(default_factory=set)
    distances: Dict[str, int] = Field(default_factory=dict)

    def __init__(self, **data):
        super().__init__(**data)
        self.add_default_actions()
        if self.current_hit_points == 0:
            self.current_hit_points = self.max_hit_points
        self._recompute_fields()


    def add_default_actions(self):
        self.add_action(Dodge(stats_block=self))
        # self.add_action(Disengage(stats_block=self))
        self.add_action(Dash(stats_block=self))
        # self.add_action(Hide(stats_block=self))
        # self.add_action(Help(stats_block=self))

    def refresh_line_of_sight(self, visible_entities: Set[str]):
        self.line_of_sight = visible_entities

    def is_in_line_of_sight(self, entity_id: str) -> bool:
        return entity_id in self.line_of_sight
    

    def refresh_distances(self, new_distances: Dict[str, int]):
        """Update the entire distances dictionary."""
        self.distances = new_distances

    def add_distance(self, target_id: str, distance: int):
        """Add or update the distance to a specific target."""
        self.distances[target_id] = distance

    def remove_distance(self, target_id: str):
        """Remove a target from the distances dictionary."""
        self.distances.pop(target_id, None)

    def is_within_distance(self, target_id: str, max_distance: int) -> bool:
        """Check if a target is within or equal to a certain distance."""
        return self.distances.get(target_id, float('inf')) <= max_distance

    def get_targets_within_distance(self, max_distance: int) -> List[str]:
        """Get all targets within or equal to a certain distance."""
        return [target_id for target_id, distance in self.distances.items() if distance <= max_distance]

    def remove_condition(self, condition_name: str):
        if condition_name in self.active_conditions:
            condition = self.active_conditions.pop(condition_name)
            condition.remove(self)
            print(f"Removed condition {condition_name} from {self.name}")
        self._recompute_fields()

    def apply_active_conditions(self):
        for condition in self.active_conditions.values():
            condition.apply(self)


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
        if condition.name not in self.active_conditions:
            print(f"Applying condition {condition.name} with ID {condition.id} to {self.name}")
            self.active_conditions[condition.name] = condition
            # condition.apply(self)
            self._recompute_fields()

    def update_conditions(self):
        print(f"Updating conditions for {self.name}")
        expired_conditions = []
        for key, condition in self.active_conditions.items():
            if condition.duration.advance():
                expired_conditions.append(key)
        
        for key in expired_conditions:
            print(f"Condition {key} expired on {self.name}")
            self.remove_condition(key)
        
        # Only recompute fields if any conditions were removed
        if expired_conditions:
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


    def perform_ability_check(self, ability: Ability, dc: int, target: Optional['StatsBlock'] = None, context: Optional[Dict[str, Any]] = None) -> bool:
        return self.ability_scores.get_ability(ability).perform_ability_check(self, dc, target, context)

    def perform_skill_check(self, skill: Skills, dc: int, target: Optional['StatsBlock'] = None, context: Optional[Dict[str, Any]] = None, return_roll: bool = False) -> Union[bool, Tuple[int, int, int]]:
        print(f"StatsBlock performing skill check for {skill.value} (StatsBlock ID: {id(self)})")
        if target:
            print(f"  Target is {target.name} (StatsBlock ID: {id(target)})")
        skill_obj = self.skills.get_skill(skill)
        result = skill_obj.perform_check(self, dc, target, context, return_roll=return_roll)
        if return_roll:
            roll, total = result
            return roll, total, dc
        return result

    def perform_saving_throw(self, ability: Ability, dc: int, target: Optional['StatsBlock'] = None, context: Optional[Dict[str, Any]] = None) -> bool:
        return self.saving_throws.perform_save(ability, self, dc, target, context)

    def causes_auto_fail_on_skill(self, skill: Skills, target: 'StatsBlock', context: Optional[Dict[str, Any]] = None) -> bool:
        skill_obj = self.skills.get_skill(skill)
        return skill_obj.bonus.causes_auto_fail(self, target, context)

    def causes_auto_success_on_skill(self, skill: Skills, target: 'StatsBlock', context: Optional[Dict[str, Any]] = None) -> bool:
        skill_obj = self.skills.get_skill(skill)
        return skill_obj.bonus.causes_auto_success(self, target, context)

    def causes_auto_fail_on_save(self, ability: Ability, target: 'StatsBlock', context: Optional[Dict[str, Any]] = None) -> bool:
        saving_throw = self.saving_throws.get_ability(ability)
        return saving_throw.bonus.causes_auto_fail(self, target, context)

    def causes_auto_success_on_save(self, ability: Ability, target: 'StatsBlock', context: Optional[Dict[str, Any]] = None) -> bool:
        saving_throw = self.saving_throws.get_ability(ability)
        return saving_throw.bonus.causes_auto_success(self, target, context)

    def add_cause_auto_fail_on_skill(self, skill: Skills, source: str, condition: ContextAwareCondition):
        skill_obj = self.skills.get_skill(skill)
        skill_obj.bonus.add_auto_fail_target_condition(source, condition)

    def add_cause_auto_success_on_skill(self, skill: Skills, source: str, condition: ContextAwareCondition):
        skill_obj = self.skills.get_skill(skill)
        skill_obj.bonus.add_auto_success_target_condition(source, condition)

    def add_cause_auto_fail_on_save(self, ability: Ability, source: str, condition: ContextAwareCondition):
        saving_throw = self.saving_throws.get_ability(ability)
        saving_throw.bonus.add_auto_fail_target_condition(source, condition)

    def add_cause_auto_success_on_save(self, ability: Ability, source: str, condition: ContextAwareCondition):
        saving_throw = self.saving_throws.get_ability(ability)
        saving_throw.bonus.add_auto_success_target_condition(source, condition)

    def remove_effect_on_skill(self, skill: Skills, source: str):
        skill_obj = self.skills.get_skill(skill)
        skill_obj.bonus.remove_effect(source)

    def remove_effect_on_save(self, ability: Ability, source: str):
        saving_throw = self.saving_throws.get_ability(ability)
        saving_throw.bonus.remove_effect(source)


    def _recompute_fields(self):
        self.armor_class.compute_base_ac(self.ability_scores)
        self._compute_passive_perception()
        self.action_economy.movement.base_value = self.speed.walk.get_value(self)
        self.action_economy.reset()
        for action in self.actions:
            if isinstance(action, Attack):
                action.update_hit_bonus()
        self.apply_active_conditions()

    def _compute_passive_perception(self):
        perception_skill = self.skills.get_skill(Skills.PERCEPTION)
        self.computed_passive_perception.base_value = 10 + perception_skill.get_bonus(self)

    def remove_cause_auto_fail_on_skill(self, skill: Skills, source: str):
        skill_obj = self.skills.get_skill(skill)
        skill_obj.bonus.remove_effect(source)

    def remove_cause_auto_fail_on_save(self, ability: Ability, source: str):
        saving_throw = self.saving_throws.get_ability(ability)
        saving_throw.bonus.remove_effect(source)

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
SelfCondition.model_rebuild()
Dodge.model_rebuild()
# # Disengage.model_rebuild()
Dash.model_rebuild()
# Hide.model_rebuild()
# Help.model_rebuild()
Attack.model_rebuild()
# ArmorClass.model_rebuild()
# Weapon.model_rebuild()