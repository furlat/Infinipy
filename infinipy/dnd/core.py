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
from infinipy.dnd.contextual import ModifiableValue, AdvantageStatus, AdvantageTracker, ContextualEffects, ContextAwareBonus, ContextAwareCondition

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

    def get_speed(self, speed_type: str, stats_block: 'StatsBlock', target: Optional['StatsBlock'] = None, context: Optional[Dict[str, Any]] = None) -> int:
        return getattr(self, speed_type).get_value(stats_block, target, context)

    def add_static_modifier(self, speed_type: str, source: str, value: int):
        getattr(self, speed_type).add_static_modifier(source, value)

    def remove_static_modifier(self, speed_type: str, source: str):
        getattr(self, speed_type).remove_static_modifier(source)

    def add_bonus(self, speed_type: str, source: str, bonus: ContextAwareBonus):
        getattr(self, speed_type).add_bonus(source, bonus)

    def add_max_constraint(self, speed_type: str, source: str, constraint: ContextAwareBonus):
        getattr(self, speed_type).add_max_constraint(source, constraint)

    def remove_effect(self, speed_type: str, source: str):
        getattr(self, speed_type).remove_effect(source)

    def set_max_speed_to_zero(self, source: str):
        for speed_type in ['walk', 'fly', 'swim', 'burrow', 'climb']:
            self.add_max_constraint(speed_type, source, lambda stats_block, target, context: 0)

    def reset_max_speed(self, source: str):
        for speed_type in ['walk', 'fly', 'swim', 'burrow', 'climb']:
            self.remove_effect(speed_type, source)



class AbilityScore(BaseModel):
    ability: Ability
    score: ModifiableValue = Field(default_factory=lambda: ModifiableValue(base_value=10))

    def get_score(self, stats_block: 'StatsBlock', target: Optional['StatsBlock'] = None, context: Optional[Dict[str, Any]] = None) -> int:
        return self.score.get_value(stats_block, target, context)

    def get_modifier(self, stats_block: 'StatsBlock', target: Optional['StatsBlock'] = None, context: Optional[Dict[str, Any]] = None) -> int:
        return (self.get_score(stats_block, target, context) - 10) // 2

    def get_advantage_status(self, stats_block: 'StatsBlock', target: Optional['StatsBlock'] = None, context: Optional[Dict[str, Any]] = None) -> AdvantageStatus:
        return self.score.get_advantage_status(stats_block, target, context)
    
    def perform_ability_check(self, stats_block: 'StatsBlock', dc: int, target: Optional['StatsBlock'] = None, context: Optional[Dict[str, Any]] = None) -> bool:
        if self.score.is_auto_fail(stats_block, target, context):
            return False
        if self.score.is_auto_success(stats_block, target, context):
            return True

        modifier = self.get_modifier(stats_block, target, context)
        advantage_status = self.get_advantage_status(stats_block, target, context)
        
        dice = Dice(dice_count=1, dice_value=20, modifier=modifier, advantage_status=advantage_status)
        roll, _ = dice.roll_with_advantage()
        return roll >= dc

    def add_bonus(self, source: str, bonus: ContextAwareBonus):
        self.score.add_bonus(source, bonus)

    def add_advantage_condition(self, source: str, condition: ContextAwareCondition):
        self.score.add_advantage_condition(source, condition)

    def add_disadvantage_condition(self, source: str, condition: ContextAwareCondition):
        self.score.add_disadvantage_condition(source, condition)

    def add_auto_fail_condition(self, source: str, condition: ContextAwareCondition):
        self.score.add_auto_fail_self_condition(source, condition)

    def add_auto_success_condition(self, source: str, condition: ContextAwareCondition):
        self.score.add_auto_success_self_condition(source, condition)

    def remove_effect(self, source: str):
        self.score.remove_effect(source)

class AbilityScores(BaseModel):
    strength: AbilityScore = Field(default_factory=lambda: AbilityScore(ability=Ability.STR, score=ModifiableValue(base_value=10)))
    dexterity: AbilityScore = Field(default_factory=lambda: AbilityScore(ability=Ability.DEX, score=ModifiableValue(base_value=10)))
    constitution: AbilityScore = Field(default_factory=lambda: AbilityScore(ability=Ability.CON, score=ModifiableValue(base_value=10)))
    intelligence: AbilityScore = Field(default_factory=lambda: AbilityScore(ability=Ability.INT, score=ModifiableValue(base_value=10)))
    wisdom: AbilityScore = Field(default_factory=lambda: AbilityScore(ability=Ability.WIS, score=ModifiableValue(base_value=10)))
    charisma: AbilityScore = Field(default_factory=lambda: AbilityScore(ability=Ability.CHA, score=ModifiableValue(base_value=10)))
    proficiency_bonus: ModifiableValue = Field(default_factory=lambda: ModifiableValue(base_value=2))
    
    def get_ability(self, ability: Ability) -> AbilityScore:
        return getattr(self, ability.value.lower())

    def get_ability_modifier(self, ability: Ability, stats_block: 'StatsBlock', target: Optional['StatsBlock'] = None, context: Optional[Dict[str, Any]] = None) -> int:
        ability_score = self.get_ability(ability)
        return ability_score.get_modifier(stats_block, target, context)

    def get_proficiency_bonus(self, ability: Ability, stats_block: 'StatsBlock', target: Optional['StatsBlock'] = None, context: Optional[Dict[str, Any]] = None) -> int:
        return self.proficiency_bonus.get_value(stats_block, target, context)

    def perform_ability_check(self, ability: Ability, stats_block: 'StatsBlock', dc: int, target: Optional['StatsBlock'] = None, context: Optional[Dict[str, Any]] = None) -> bool:
        ability_score = self.get_ability(ability)
        return ability_score.perform_ability_check(stats_block, dc, target, context)

ABILITY_TO_SKILLS = {
    Ability.STR: [Skills.ATHLETICS],
    Ability.DEX: [Skills.ACROBATICS, Skills.SLEIGHT_OF_HAND, Skills.STEALTH],
    Ability.CON: [],
    Ability.INT: [Skills.ARCANA, Skills.HISTORY, Skills.INVESTIGATION, Skills.NATURE, Skills.RELIGION],
    Ability.WIS: [Skills.ANIMAL_HANDLING, Skills.INSIGHT, Skills.MEDICINE, Skills.PERCEPTION, Skills.SURVIVAL],
    Ability.CHA: [Skills.DECEPTION, Skills.INTIMIDATION, Skills.PERFORMANCE, Skills.PERSUASION]
}

class Skill(BaseModel):
    ability: Ability
    skill: Skills
    proficient: bool = False
    expertise: bool = False
    bonus: ModifiableValue = Field(default_factory=lambda: ModifiableValue(base_value=0))

    def get_bonus(self, stats_block: 'StatsBlock', target: Optional['StatsBlock'] = None, context: Optional[Dict[str, Any]] = None) -> int:
        ability_bonus = stats_block.ability_scores.get_ability_modifier(self.ability, stats_block, target, context)
        proficiency_bonus = stats_block.ability_scores.get_proficiency_bonus(self.ability, stats_block, target, context)
        if self.expertise:
            proficiency_bonus *= 2
        elif not self.proficient:
            proficiency_bonus = 0
        self.bonus.base_value = ability_bonus + proficiency_bonus
        return self.bonus.get_value(stats_block, target, context)

    def get_advantage_status(self, stats_block: 'StatsBlock', target: Optional['StatsBlock'] = None, context: Optional[Dict[str, Any]] = None) -> AdvantageStatus:
        return self.bonus.get_advantage_status(stats_block, target, context)

    def perform_check(self, stats_block: 'StatsBlock', dc: int, target: Optional['StatsBlock'] = None, context: Optional[Dict[str, Any]] = None, return_roll: bool = False) -> Union[bool, Tuple[int, int]]:
        print(f"Performing {self.ability.value} skill check")
        
        if self.bonus.is_auto_fail(stats_block, target, context):
            print(f"Auto-fail condition met for {self.skill.value} check")
            return (1, 1) if return_roll else False
        
        if self.bonus.is_auto_success(stats_block, target, context):
            print(f"Auto-success condition met for {self.skill.value} check")
            return (20, 20) if return_roll else True

        bonus = self.get_bonus(stats_block, target, context)
        
        # Create a combined AdvantageTracker
        advantage_tracker = AdvantageTracker()
        self.bonus.self_effects.apply_advantage_disadvantage(stats_block, target, advantage_tracker, context)
        if target:
            #get the skill of the target
            target_skill = target.skills.get_skill(self.skill)
            target_skill.bonus.target_effects.apply_advantage_disadvantage(target, stats_block, advantage_tracker, context)
        
        advantage_status = advantage_tracker.status
        
        print(f"Bonus: {bonus}, Advantage status: {advantage_status}")
        dice = Dice(dice_count=1, dice_value=20, modifier=bonus, advantage_status=advantage_status)
        roll, _ = dice.roll_with_advantage()
        total = roll + bonus
        print(f"Roll: {roll}, Total: {total}, DC: {dc}")
        if return_roll:
            return roll, total
        return total >= dc
    
    # Self effects
    def add_self_bonus(self, source: str, bonus: ContextAwareBonus):
        self.bonus.self_effects.add_bonus(source, bonus)

    def add_self_advantage_condition(self, source: str, condition: ContextAwareCondition):
        self.bonus.self_effects.add_advantage_condition(source, condition)

    def add_self_disadvantage_condition(self, source: str, condition: ContextAwareCondition):
        self.bonus.self_effects.add_disadvantage_condition(source, condition)

    def add_self_auto_fail_condition(self, source: str, condition: ContextAwareCondition):
        self.bonus.self_effects.add_auto_fail_self_condition(source, condition)

    def add_self_auto_success_condition(self, source: str, condition: ContextAwareCondition):
        self.bonus.self_effects.add_auto_success_self_condition(source, condition)

    # Target effects
    def add_target_bonus(self, source: str, bonus: ContextAwareBonus):
        self.bonus.target_effects.add_bonus(source, bonus)

    def add_target_advantage_condition(self, source: str, condition: ContextAwareCondition):
        self.bonus.target_effects.add_advantage_condition(source, condition)

    def add_target_disadvantage_condition(self, source: str, condition: ContextAwareCondition):
        self.bonus.target_effects.add_disadvantage_condition(source, condition)

    def add_target_auto_fail_condition(self, source: str, condition: ContextAwareCondition):
        self.bonus.target_effects.add_auto_fail_self_condition(source, condition)

    def add_target_auto_success_condition(self, source: str, condition: ContextAwareCondition):
        self.bonus.target_effects.add_auto_success_self_condition(source, condition)

    # Remove effects
    def remove_self_effect(self, source: str):
        self.bonus.self_effects.remove_effect(source)

    def remove_target_effect(self, source: str):
        self.bonus.target_effects.remove_effect(source)

    def remove_all_effects(self, source: str):
        self.remove_self_effect(source)
        self.remove_target_effect(source)

class SkillSet(BaseModel):
    acrobatics: Skill = Field(default_factory=lambda: Skill(ability=Ability.DEX, skill=Skills.ACROBATICS))
    animal_handling: Skill = Field(default_factory=lambda: Skill(ability=Ability.WIS, skill=Skills.ANIMAL_HANDLING))
    arcana: Skill = Field(default_factory=lambda: Skill(ability=Ability.INT, skill=Skills.ARCANA))
    athletics: Skill = Field(default_factory=lambda: Skill(ability=Ability.STR, skill=Skills.ATHLETICS))
    deception: Skill = Field(default_factory=lambda: Skill(ability=Ability.CHA, skill=Skills.DECEPTION))
    history: Skill = Field(default_factory=lambda: Skill(ability=Ability.INT, skill=Skills.HISTORY))
    insight: Skill = Field(default_factory=lambda: Skill(ability=Ability.WIS, skill=Skills.INSIGHT))
    intimidation: Skill = Field(default_factory=lambda: Skill(ability=Ability.CHA, skill=Skills.INTIMIDATION))
    investigation: Skill = Field(default_factory=lambda: Skill(ability=Ability.INT, skill=Skills.INVESTIGATION))
    medicine: Skill = Field(default_factory=lambda: Skill(ability=Ability.WIS, skill=Skills.MEDICINE))
    nature: Skill = Field(default_factory=lambda: Skill(ability=Ability.INT, skill=Skills.NATURE))
    perception: Skill = Field(default_factory=lambda: Skill(ability=Ability.WIS, skill=Skills.PERCEPTION))
    performance: Skill = Field(default_factory=lambda: Skill(ability=Ability.CHA, skill=Skills.PERFORMANCE))
    persuasion: Skill = Field(default_factory=lambda: Skill(ability=Ability.CHA, skill=Skills.PERSUASION))
    religion: Skill = Field(default_factory=lambda: Skill(ability=Ability.INT, skill=Skills.RELIGION))
    sleight_of_hand: Skill = Field(default_factory=lambda: Skill(ability=Ability.DEX, skill=Skills.SLEIGHT_OF_HAND))
    stealth: Skill = Field(default_factory=lambda: Skill(ability=Ability.DEX, skill=Skills.STEALTH))
    survival: Skill = Field(default_factory=lambda: Skill(ability=Ability.WIS, skill=Skills.SURVIVAL))
    proficiencies: Set[Skills] = Field(default_factory=set)
    expertise: Set[Skills] = Field(default_factory=set)

    def get_skill(self, skill: Skills) -> Skill:
        attribute_name = skill.value.lower().replace(' ', '_')
        return getattr(self, attribute_name)
    
    def set_proficiency(self, skill: Skills):
        self.proficiencies.add(skill)
        self.get_skill(skill).proficient = True

    def set_expertise(self, skill: Skills):
        self.expertise.add(skill)
        self.get_skill(skill).expertise = True
    
    def add_effect_to_all_skills(self, effect_type: str, source: str, effect: Union[ContextAwareBonus, ContextAwareCondition]):
        for skill in Skills:
            skill_obj = self.get_skill(skill)
            getattr(skill_obj, f"add_{effect_type}")(source, effect)

    def remove_effect_from_all_skills(self, effect_type: str, source: str):
        for skill in Skills:
            skill_obj = self.get_skill(skill)
            getattr(skill_obj, f"remove_{effect_type}_effect")(source)

    def remove_all_effects_from_all_skills(self, source: str):
        for skill in Skills:
            skill_obj = self.get_skill(skill)
            skill_obj.remove_all_effects(source)

    def perform_skill_check(self, skill: Skills, stats_block: 'StatsBlock', dc: int, target: Optional['StatsBlock'] = None, context: Optional[Dict[str, Any]] = None) -> bool:
        return self.get_skill(skill).perform_check(stats_block, dc, target, context)


class SavingThrow(BaseModel):
    ability: Ability
    proficient: bool
    bonus: ModifiableValue = Field(default_factory=lambda: ModifiableValue(base_value=0))

    def get_bonus(self, stats_block: 'StatsBlock', target: Optional['StatsBlock'] = None, context: Optional[Dict[str, Any]] = None) -> int:
        ability_bonus = stats_block.ability_scores.get_ability_modifier(self.ability, stats_block, target, context)
        proficiency_bonus = stats_block.ability_scores.proficiency_bonus.get_value(stats_block, target, context) if self.proficient else 0
        return ability_bonus + proficiency_bonus
    
    def get_advantage_status(self, stats_block: 'StatsBlock', target: Optional['StatsBlock'] = None, context: Optional[Dict[str, Any]] = None) -> AdvantageStatus:
        return self.bonus.get_advantage_status(stats_block, target, context)
    
    def perform_save(self, stats_block: 'StatsBlock', dc: int, target: Optional['StatsBlock'] = None, context: Optional[Dict[str, Any]] = None) -> bool:
        if self.bonus.is_auto_fail(stats_block, target, context):
            print(f"Auto-fail condition met for {self.ability.value} saving throw")
            return False
        
        if self.bonus.is_auto_success(stats_block, target, context):
            print(f"Auto-success condition met for {self.ability.value} saving throw")
            return True

        bonus = self.get_bonus(stats_block, target, context)
        # Create a combined AdvantageTracker
        advantage_tracker = AdvantageTracker()
        self.bonus.self_effects.apply_advantage_disadvantage(stats_block, target, advantage_tracker, context)
        if target:
            #get the skill of the target
            target_skill = target.saving_throws.get_ability(self.ability)
            target_skill.bonus.target_effects.apply_advantage_disadvantage(target, stats_block, advantage_tracker, context)
        
        advantage_status = advantage_tracker.status

        dice = Dice(dice_count=1, dice_value=20, modifier=bonus, advantage_status=advantage_status)
        roll, _ = dice.roll_with_advantage()
        total = roll + bonus
        print(f"Saving Throw: {self.ability.value}, Roll: {roll}, Total: {total}, DC: {dc}")
        return total >= dc

    def add_bonus(self, source: str, bonus: ContextAwareBonus):
        self.bonus.add_bonus(source, bonus)

    def add_advantage_condition(self, source: str, condition: ContextAwareCondition):
        self.bonus.add_advantage_condition(source, condition)

    def add_disadvantage_condition(self, source: str, condition: ContextAwareCondition):
        self.bonus.add_disadvantage_condition(source, condition)

    def add_auto_fail_condition(self, source: str, condition: ContextAwareCondition):
        self.bonus.add_auto_fail_self_condition(source, condition)

    def add_auto_success_condition(self, source: str, condition: ContextAwareCondition):
        self.bonus.add_auto_success_self_condition(source, condition)

    def remove_effect(self, source: str):
        self.bonus.remove_effect(source)


class SavingThrows(BaseModel):
    strength: SavingThrow = Field(default_factory=lambda: SavingThrow(ability=Ability.STR, proficient=False))
    dexterity: SavingThrow = Field(default_factory=lambda: SavingThrow(ability=Ability.DEX, proficient=False))
    constitution: SavingThrow = Field(default_factory=lambda: SavingThrow(ability=Ability.CON, proficient=False))
    intelligence: SavingThrow = Field(default_factory=lambda: SavingThrow(ability=Ability.INT, proficient=False))
    wisdom: SavingThrow = Field(default_factory=lambda: SavingThrow(ability=Ability.WIS, proficient=False))
    charisma: SavingThrow = Field(default_factory=lambda: SavingThrow(ability=Ability.CHA, proficient=False))

    def get_ability(self, ability: Ability) -> SavingThrow:
        return getattr(self, ability.value.lower())

    def set_proficiency(self, ability: Ability, value: bool = True):
        savingthrow = self.get_ability(ability)
        savingthrow.proficient = value
    
    def add_auto_fail_condition(self, ability: Ability, source: str, condition: ContextAwareCondition):
        saving_throw = self.get_ability(ability)
        saving_throw.add_auto_fail_condition(source, condition)

    def add_auto_success_condition(self, ability: Ability, source: str, condition: ContextAwareCondition):
        saving_throw = self.get_ability(ability)
        saving_throw.add_auto_success_condition(source, condition)

    def remove_effect(self, ability: Ability, source: str):
        saving_throw = self.get_ability(ability)
        saving_throw.remove_effect(source)

    def perform_save(self, ability: Ability, stats_block: 'StatsBlock', dc: int, target: Optional['StatsBlock'] = None, context: Optional[Dict[str, Any]] = None) -> bool:
        return self.get_ability(ability).perform_save(stats_block, dc, target, context)

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
    has_advanced: bool = False

    def advance(self) -> bool:
        if self.type in [DurationType.ROUNDS, DurationType.MINUTES, DurationType.HOURS]:
            if isinstance(self.time, int):
                self.time -= 1
                return self.time <= 0
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

    def set_max_actions(self, source: str, value: int):
        self.actions.add_max_constraint(source, lambda stats_block, target, context: value)

    def set_max_bonus_actions(self, source: str, value: int):
        self.bonus_actions.add_max_constraint(source, lambda stats_block, target, context: value)

    def set_max_reactions(self, source: str, value: int):
        self.reactions.add_max_constraint(source, lambda stats_block, target, context: value)

    def reset_max_actions(self, source: str):
        self.actions.remove_effect(source)

    def reset_max_bonus_actions(self, source: str):
        self.bonus_actions.remove_effect(source)

    def reset_max_reactions(self, source: str):
        self.reactions.remove_effect(source)

    def modify_movement(self, source: str, value: int):
        self.movement.add_static_modifier(source, value)

    def remove_movement_modifier(self, source: str):
        self.movement.remove_static_modifier(source)