from pydantic import BaseModel, Field
from typing import Optional, TYPE_CHECKING, Dict, Any, Tuple
import uuid
from infinipy.dnd.core import Duration, DurationType, HEARING_DEPENDENT_ABILITIES, Skills, Ability, SensesType
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
# | **Blinded**   V          | Cannot see, automatically fails any check requiring sight, attack rolls have disadvantage.                  | `Attack`: Add ability to apply disadvantage; `AbilityCheck`: Add failure condition for sight-related checks.                |
# | **Charmed**   V          | Cannot attack the charmer, the charmer has advantage on social interactions.                                | `Attack`: Add logic to prevent attacking charmer; `AbilityCheck`: Add advantage for social interactions with charmer.       |
# | **Deafened**            | Cannot hear, automatically fails any check requiring hearing.                                               | `AbilityCheck`: Add failure condition for hearing-related checks.                                                           |
# | **Frightened**   V       | Disadvantage on ability checks and attack rolls while the source of fear is in sight.                       | `Attack`: Add ability to apply disadvantage; `AbilityCheck`: Add ability to apply disadvantage.                              |
# | **Grappled**      V      | Speed becomes 0, can't benefit from any bonus to speed.                                                     | `Speed`: Add logic to set speed to 0.                                                                                       |
# | **Incapacitated**   V    | Cannot take actions or reactions.                                                                           | `ActionEconomy`: Add logic to block actions and reactions.                                                                  |
# | **Invisible**           | Impossible to see without special sense, attacks against have disadvantage, attacks have advantage.         | `Attack`: Add ability to apply advantage/disadvantage.                                                                      |
# | **Paralyzed**           | Incapacitated, can't move or speak, automatically fails Strength and Dexterity saves, attacks have advantage. | `ActionEconomy`: Add logic to block actions and reactions; `Speed`: Add logic to set speed to 0; `SavingThrow`: Add failure condition. |
# | **Petrified**           | Transformed into solid inanimate substance, incapacitated, and unaware of surroundings.                     | `ActionEconomy`: Add logic to block actions and reactions; `Speed`: Add logic to set speed to 0; `SavingThrow`: Add failure condition. |
# | **Poisoned**    V        | Disadvantage on attack rolls and ability checks.                                                            | `Attack`: Add ability to apply disadvantage; `AbilityCheck`: Add ability to apply disadvantage.                              |
# | **Prone**               | Disadvantage on attack rolls, attacks within 5 feet have advantage, others have disadvantage.               | `Attack`: Add ability to apply advantage/disadvantage.                                                                      |
# | **Restrained**   V       | Speed becomes 0, attack rolls have disadvantage, Dexterity saves have disadvantage.                         | `Speed`: Add logic to set speed to 0; `Attack`: Add ability to apply disadvantage; `SavingThrow`: Add ability to apply disadvantage. |
# | **Stunned**             | Incapacitated, can't move, can speak only falteringly.                                                      | `ActionEconomy`: Add logic to block actions and reactions; `Speed`: Add logic to set speed to 0; `SavingThrow`: Add failure condition. |
# | **Unconscious**         | Incapacitated, can't move or speak, unaware of surroundings, drops held items, falls prone.                | `ActionEconomy`: Add logic to block actions and reactions; `Speed`: Add logic to set speed to 0; `SavingThrow`: Add failure condition. |
# | **Dodging**      V       | Attacks against have disadvantage, Dexterity saves have advantage.                                          | `Attack`: Add ability to apply disadvantage; `SavingThrow`: Add ability to apply advantage.                                  |
# | **Dashing**     V        | Movement increases by an additional speed.                                                                  | `Speed`: Add logic to increase movement.                                                                                    |
# | **Hiding**              | Makes Dexterity (Stealth) checks to hide.                                                                   | `AbilityCheck`: Add logic for hiding mechanic.                                                                              |
# | **Helping**             | Lends aid to another creature, giving advantage on next ability check or attack roll.                       | `Attack`: Add ability to apply advantage; `AbilityCheck`: Add ability to apply advantage.                                   |



class Blinded(Condition):
    name: str = "Blinded"

    def apply(self, stats_block: 'StatsBlock') -> None:
        print(f"Applying Blinded condition to {stats_block.name}")
        
        # Add disadvantage to all attacks
        for action in stats_block.actions:
            if isinstance(action, Attack):
                action.hit_bonus.add_disadvantage_condition("Blinded", self.blinded_check)
        
        # Give advantage to all attacks against this creature
        stats_block.armor_class.add_opponent_advantage_condition("Blinded", self.blinded_check)

        # Add auto-fail condition for sight-based ability checks
        for skill in Skills:
            skill_obj = stats_block.skills.get_skill(skill)
            skill_obj.add_self_auto_fail_condition("Blinded", self.blinded_sight_check)

    def remove(self, stats_block: 'StatsBlock') -> None:
        print(f"Removing Blinded condition from {stats_block.name}")
        
        # Remove disadvantage from all attacks
        for action in stats_block.actions:
            if isinstance(action, Attack):
                action.hit_bonus.remove_effect("Blinded")
        
        # Remove advantage from all attacks against this creature
        stats_block.armor_class.remove_opponent_advantage_condition("Blinded")

        # Remove auto-fail condition from all skills
        for skill in Skills:
            skill_obj = stats_block.skills.get_skill(skill)
            skill_obj.remove_all_effects("Blinded")

    @staticmethod
    def blinded_check(source: 'StatsBlock', target: Optional['StatsBlock'], context: Optional[Dict[str, Any]] = None) -> bool:
        return True  # Always apply the effect when blinded

    @staticmethod
    def blinded_sight_check(source: 'StatsBlock', target: Optional['StatsBlock'], context: Optional[Dict[str, Any]] = None) -> bool:
        # Check if the context indicates this is a sight-based check
        if context and context.get('requires_sight', False):
            return True  # Auto-fail sight-based checks
        return False  # Don't auto-fail other checks

class Charmed(Condition):
    name: str = "Charmed"
    source_entity_id: str

    def apply(self, stats_block: 'StatsBlock') -> None:
        print(f"Applying Charmed condition to {stats_block.name}")
        # Prevent attacking the charmer
        for action in stats_block.actions:
            if isinstance(action, Attack):
                action.add_auto_fail_condition("Charmed", self.charmed_attack_check)

        social_skills = [Skills.DECEPTION, Skills.INTIMIDATION, Skills.PERFORMANCE, Skills.PERSUASION]
        for skill in social_skills:
            skill_obj = stats_block.skills.get_skill(skill)
            print(f"Adding Charmed advantage condition to {skill.value} for {stats_block.name}")
            skill_obj.add_target_advantage_condition("Charmed", self.charmed_social_check)

    def remove(self, stats_block: 'StatsBlock') -> None:
        print(f"Removing Charmed condition from {stats_block.name}")
        # Remove attack restriction
        for action in stats_block.actions:
            if isinstance(action, Attack):
                action.remove_effect("Charmed")

        # Remove social check advantage
        social_skills = [Skills.DECEPTION, Skills.INTIMIDATION, Skills.PERFORMANCE, Skills.PERSUASION]
        for skill in social_skills:
            skill_obj = stats_block.skills.get_skill(skill)
            skill_obj.remove_target_effect("Charmed")

    @staticmethod
    def charmed_social_check(source: 'StatsBlock', target: Optional['StatsBlock'], context: Optional[Dict[str, Any]] = None) -> bool:
        if target and "Charmed" in source.active_conditions and source.active_conditions["Charmed"].source_entity_id == target.id:
            return True
        return False

    @staticmethod
    def charmed_attack_check(source: 'StatsBlock', target: Optional['StatsBlock'], context: Optional[Dict[str, Any]] = None) -> bool:
        if target and "Charmed" in source.active_conditions and target.id == source.active_conditions["Charmed"].source_entity_id:
            return True
        return False

class Deafened(Condition):
    name: str = "Deafened"

    def apply(self, stats_block: 'StatsBlock') -> None:
        print(f"Applying Deafened condition to {stats_block.name}")
        
        # Add auto-fail condition for hearing-based ability checks
        for skill in Skills:
            skill_obj = stats_block.skills.get_skill(skill)
            skill_obj.add_self_auto_fail_condition("Deafened", self.deafened_hearing_check)

    def remove(self, stats_block: 'StatsBlock') -> None:
        print(f"Removing Deafened condition from {stats_block.name}")
        
        # Remove auto-fail condition from all skills
        for skill in Skills:
            skill_obj = stats_block.skills.get_skill(skill)
            skill_obj.remove_all_effects("Deafened")

    @staticmethod
    def deafened_hearing_check(source: 'StatsBlock', target: Optional['StatsBlock'], context: Optional[Dict[str, Any]] = None) -> bool:
        # Check if the context indicates this is a hearing-based check
        if context and context.get('requires_hearing', False):
            return True  # Auto-fail hearing-based checks
        return False  # Don't auto-fail other checks

class Frightened(Condition):
    name: str = "Frightened"
    source_entity_id: str

    def apply(self, stats_block: 'StatsBlock') -> None:
        print(f"Applying Frightened condition to {stats_block.name}")
        
        # Add disadvantage to all attacks
        for action in stats_block.actions:
            if isinstance(action, Attack):
                action.add_contextual_disadvantage("Frightened", self.frightened_check)
        
        # Add disadvantage to all ability checks
        for ability in Ability:
            ability_score = stats_block.ability_scores.get_ability(ability)
            ability_score.add_disadvantage_condition("Frightened", self.frightened_check)

    def remove(self, stats_block: 'StatsBlock') -> None:
        print(f"Removing Frightened condition from {stats_block.name}")
        
        # Remove disadvantage from all attacks
        for action in stats_block.actions:
            if isinstance(action, Attack):
                action.remove_effect("Frightened")
        
        # Remove disadvantage from all ability checks
        for ability in Ability:
            ability_score = stats_block.ability_scores.get_ability(ability)
            ability_score.remove_effect("Frightened")

    @staticmethod
    def frightened_check(source: 'StatsBlock', target: Optional['StatsBlock'], context: Optional[Dict[str, Any]] = None) -> bool:
        if "Frightened" in source.active_conditions:
            frightened_condition = source.active_conditions["Frightened"]
            return source.is_in_line_of_sight(frightened_condition.source_entity_id)
        return False


class Grappled(Condition):
    name: str = "Grappled"
    source_entity_id: str

    def apply(self, stats_block: 'StatsBlock') -> None:
        print(f"Applying Grappled condition to {stats_block.name}")
        stats_block.speed.set_max_speed_to_zero("Grappled")

    def remove(self, stats_block: 'StatsBlock') -> None:
        print(f"Removing Grappled condition from {stats_block.name}")
        stats_block.speed.reset_max_speed("Grappled")

class Incapacitated(Condition):
    name: str = "Incapacitated"

    def apply(self, stats_block: 'StatsBlock') -> None:
        print(f"Applying Incapacitated condition to {stats_block.name}")
        stats_block.action_economy.set_max_actions("Incapacitated", 0)
        stats_block.action_economy.set_max_bonus_actions("Incapacitated", 0)
        stats_block.action_economy.set_max_reactions("Incapacitated", 0)

    def remove(self, stats_block: 'StatsBlock') -> None:
        print(f"Removing Incapacitated condition from {stats_block.name}")
        stats_block.action_economy.reset_max_actions("Incapacitated")
        stats_block.action_economy.reset_max_bonus_actions("Incapacitated")
        stats_block.action_economy.reset_max_reactions("Incapacitated")

class Invisible(Condition):
    name: str = "Invisible"

    def apply(self, stats_block: 'StatsBlock') -> None:
        print(f"Applying Invisible condition to {stats_block.name}")
        
        # Add advantage to all attacks
        for action in stats_block.actions:
            if isinstance(action, Attack):
                action.add_contextual_advantage("Invisible", self.invisible_offensive_check)
        
        # Give disadvantage to all attacks against this creature
        stats_block.armor_class.add_opponent_disadvantage_condition("Invisible", self.invisible_defensive_check)

    def remove(self, stats_block: 'StatsBlock') -> None:
        print(f"Removing Invisible condition from {stats_block.name}")
        
        # Remove advantage from all attacks
        for action in stats_block.actions:
            if isinstance(action, Attack):
                action.remove_effect("Invisible")
        
        # Remove disadvantage from all attacks against this creature
        stats_block.armor_class.remove_opponent_disadvantage_condition("Invisible")

    @staticmethod
    def can_see_invisible(observer: 'StatsBlock', target: 'StatsBlock') -> bool:
        observer_senses = {sense.type for sense in observer.senses}
        return SensesType.TRUESIGHT in observer_senses or SensesType.TREMORSENSE in observer_senses

    @staticmethod
    def invisible_offensive_check(source: 'StatsBlock', target: Optional['StatsBlock'], context: Optional[Dict[str, Any]] = None) -> bool:
        if target is None:
            print("No target provided for invisible check")
            return True  # If no target, assume advantage applies
        if Invisible.can_see_invisible(target, source) and target.is_in_line_of_sight(source.id):
            print(f"{target.name} can see invisible {source.name}")
            return False
        print(f"{target.name} cannot see invisible {source.name}")
        return True
    
    @staticmethod
    def invisible_defensive_check(source: 'StatsBlock', target: Optional['StatsBlock'], context: Optional[Dict[str, Any]] = None) -> bool:
        if target is None:
            print("No target provided for invisible check")
            return True  # If no target, assume advantage applies
        if Invisible.can_see_invisible(source, target) and source.is_in_line_of_sight(target.id):
            print(f"{source.name} can see invisible {target.name}")
            return False
        print(f"{source.name} cannot see invisible {target.name}")
        return True
    
class Paralyzed(Condition):
    name: str = "Paralyzed"

    def apply(self, stats_block: 'StatsBlock') -> None:
        print(f"Applying Paralyzed condition to {stats_block.name}")
        
        # Incapacitated effects (can't take actions or reactions)
        stats_block.action_economy.set_max_actions("Paralyzed", 0)
        stats_block.action_economy.set_max_bonus_actions("Paralyzed", 0)
        stats_block.action_economy.set_max_reactions("Paralyzed", 0)
        
        # Can't move
        stats_block.speed.set_max_speed_to_zero("Paralyzed")
        
        # Auto-fail STR and DEX saves
        stats_block.saving_throws.get_ability(Ability.STR).add_auto_fail_condition("Paralyzed", self.paralyzed_check)
        stats_block.saving_throws.get_ability(Ability.DEX).add_auto_fail_condition("Paralyzed", self.paralyzed_check)
        
        # Any attack that hits the creature is a critical hit if the attacker is within 5 feet of the creature
        stats_block.armor_class.add_opponent_auto_critical_condition("Paralyzed", self.paralyzed_attack_check)

    def remove(self, stats_block: 'StatsBlock') -> None:
        print(f"Removing Paralyzed condition from {stats_block.name}")
        
        # Remove Incapacitated effects
        stats_block.action_economy.reset_max_actions("Paralyzed")
        stats_block.action_economy.reset_max_bonus_actions("Paralyzed")
        stats_block.action_economy.reset_max_reactions("Paralyzed")
        
        # Remove movement restriction
        stats_block.speed.reset_max_speed("Paralyzed")
        
        # Remove auto-fail on STR and DEX saves
        stats_block.saving_throws.get_ability(Ability.STR).remove_effect("Paralyzed")
        stats_block.saving_throws.get_ability(Ability.DEX).remove_effect("Paralyzed")
        
        # Remove auto-critical condition
        stats_block.armor_class.remove_opponent_auto_critical_condition("Paralyzed")

    @staticmethod
    def paralyzed_check(source: 'StatsBlock', target: Optional['StatsBlock'], context: Optional[Dict[str, Any]] = None) -> bool:
        return True  # Always apply the effect when paralyzed
    
    @staticmethod
    def paralyzed_attack_check(source: 'StatsBlock', target: Optional['StatsBlock'], context: Optional[Dict[str, Any]] = None) -> bool:
        if target is None or source is None:
            return False
        return target.is_within_distance(source.id, 5)  # 5 feet for melee range
    
class Poisoned(Condition):
    name: str = "Poisoned"

    def apply(self, stats_block: 'StatsBlock') -> None:
        print(f"Applying Poisoned condition to {stats_block.name}")
        
        # Add disadvantage to all attacks
        for action in stats_block.actions:
            if isinstance(action, Attack):
                action.hit_bonus.self_effects.add_disadvantage_condition("Poisoned", self.poisoned_check)
        
        # Add disadvantage to all ability checks (which includes skill checks)
        for skill in Skills:
            skill_obj = stats_block.skills.get_skill(skill)
            skill_obj.bonus.self_effects.add_disadvantage_condition("Poisoned", self.poisoned_check)

    def remove(self, stats_block: 'StatsBlock') -> None:
        print(f"Removing Poisoned condition from {stats_block.name}")
        
        # Remove disadvantage from all attacks
        for action in stats_block.actions:
            if isinstance(action, Attack):
                action.hit_bonus.self_effects.remove_effect("Poisoned")
        
        # Remove disadvantage from all ability checks
        for skill in Skills:
            skill_obj = stats_block.skills.get_skill(skill)
            skill_obj.bonus.self_effects.remove_effect("Poisoned")

    @staticmethod
    def poisoned_check(source: 'StatsBlock', target: Optional['StatsBlock'] = None,  context: Optional[Dict[str, Any]] = None) -> bool:
        return True  # Always apply disadvantage when poisoned

class Stunned(Condition):
    name: str = "Stunned"

    def apply(self, stats_block: 'StatsBlock') -> None:
        print(f"Applying Stunned condition to {stats_block.name}")
        
        # Incapacitated effects (can't take actions or reactions)
        stats_block.action_economy.set_max_actions("Stunned", 0)
        stats_block.action_economy.set_max_bonus_actions("Stunned", 0)
        stats_block.action_economy.set_max_reactions("Stunned", 0)
        
        # Can't move
        stats_block.speed.set_max_speed_to_zero("Stunned")
        
        # Auto-fail STR and DEX saves
        stats_block.saving_throws.get_ability(Ability.STR).add_auto_fail_condition("Stunned", self.stunned_check)
        stats_block.saving_throws.get_ability(Ability.DEX).add_auto_fail_condition("Stunned", self.stunned_check)
        
        # Advantage on attacks against this creature
        stats_block.armor_class.add_opponent_advantage_condition("Stunned", self.stunned_check)

    def remove(self, stats_block: 'StatsBlock') -> None:
        print(f"Removing Stunned condition from {stats_block.name}")
        
        # Remove Incapacitated effects
        stats_block.action_economy.reset_max_actions("Stunned")
        stats_block.action_economy.reset_max_bonus_actions("Stunned")
        stats_block.action_economy.reset_max_reactions("Stunned")
        
        # Remove movement restriction
        stats_block.speed.reset_max_speed("Stunned")
        
        # Remove auto-fail on STR and DEX saves
        stats_block.saving_throws.get_ability(Ability.STR).remove_effect("Stunned")
        stats_block.saving_throws.get_ability(Ability.DEX).remove_effect("Stunned")
        
        # Remove advantage on attacks against this creature
        stats_block.armor_class.remove_opponent_advantage_condition("Stunned")

    @staticmethod
    def stunned_check(source: 'StatsBlock', target: Optional['StatsBlock'], context: Optional[Dict[str, Any]] = None) -> bool:
        return True  # Always apply the effect when stunned

class Restrained(Condition):
    name: str = "Restrained"

    def apply(self, stats_block: 'StatsBlock') -> None:
        print(f"Applying Restrained condition to {stats_block.name}")
        
        # Set speed to 0
        stats_block.speed.set_max_speed_to_zero("Restrained")
        
        # Add disadvantage to all attacks
        for action in stats_block.actions:
            if isinstance(action, Attack):
                action.hit_bonus.self_effects.add_disadvantage_condition("Restrained", self.restrained_check)
        
        # Add disadvantage to Dexterity saving throws
        dex_save = stats_block.saving_throws.get_ability(Ability.DEX)
        dex_save.bonus.self_effects.add_disadvantage_condition("Restrained", self.restrained_check)

    def remove(self, stats_block: 'StatsBlock') -> None:
        print(f"Removing Restrained condition from {stats_block.name}")
        
        # Reset speed
        stats_block.speed.reset_max_speed("Restrained")
        
        # Remove disadvantage from all attacks
        for action in stats_block.actions:
            if isinstance(action, Attack):
                action.hit_bonus.self_effects.remove_effect("Restrained")
        
        # Remove disadvantage from Dexterity saving throws
        dex_save = stats_block.saving_throws.get_ability(Ability.DEX)
        dex_save.bonus.self_effects.remove_effect("Restrained")

    @staticmethod
    def restrained_check(source: 'StatsBlock', target: Optional['StatsBlock'] = None,  context: Optional[Dict[str, Any]] = None) -> bool:
        return True  # Always apply disadvantage when restrained


class Dodging(Condition):
    name: str = "Dodging"

    def apply(self, stats_block: 'StatsBlock') -> None:
        print(f"Applying Dodging condition to {stats_block.name}")
        
        # Add disadvantage to attacks against this creature
        stats_block.armor_class.base_ac.target_effects.add_disadvantage_condition("Dodging", self.dodging_check)
        
        # Add advantage to Dexterity saving throws
        dex_save = stats_block.saving_throws.get_ability(Ability.DEX)
        dex_save.bonus.self_effects.add_advantage_condition("Dodging", self.dodging_check)

    def remove(self, stats_block: 'StatsBlock') -> None:
        print(f"Removing Dodging condition from {stats_block.name}")
        
        # Remove disadvantage from attacks against this creature
        stats_block.armor_class.base_ac.target_effects.remove_effect("Dodging")
        
        # Remove advantage from Dexterity saving throws
        dex_save = stats_block.saving_throws.get_ability(Ability.DEX)
        dex_save.bonus.self_effects.remove_effect("Dodging")

    @staticmethod
    def dodging_check(source: 'StatsBlock', target: Optional['StatsBlock'] = None,  context: Optional[Dict[str, Any]] = None) -> bool:
        return True  # Always apply the effect when dodging
    
class Dashing(Condition):
    name: str = "Dashing"

    def apply(self, stats_block: 'StatsBlock') -> None:
        print(f"Applying Dashing condition to {stats_block.name}")
        
        # Double the movement speed
        for speed_type in ['walk', 'fly', 'swim', 'burrow', 'climb']:
            current_speed = stats_block.speed.get_speed(speed_type, stats_block)
            stats_block.speed.add_static_modifier(speed_type, "Dashing", current_speed)

    def remove(self, stats_block: 'StatsBlock') -> None:
        print(f"Removing Dashing condition from {stats_block.name}")
        
        # Remove the speed bonus
        for speed_type in ['walk', 'fly', 'swim', 'burrow', 'climb']:
            stats_block.speed.remove_static_modifier(speed_type, "Dashing")

    @staticmethod
    def dashing_check(source: 'StatsBlock', target: Optional['StatsBlock'] = None,  context: Optional[Dict[str, Any]] = None) -> bool:
        return True  # Always apply the effect when dashing
    
