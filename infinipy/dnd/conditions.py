from pydantic import BaseModel, Field
from typing import Optional, TYPE_CHECKING, Dict, Any, Tuple
import uuid
from infinipy.dnd.core import Duration, DurationType, HEARING_DEPENDENT_ABILITIES, Skills, Ability
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

# difficult - will require more core functionality to be implemented first:
# Deafened requires a "tag" system for ability checks to be implemented, this could be arbitrary strings that can be added to ability checks to indicate that they are hearing-dependent or any other qualitative descriptor.
# Frightened requires a "line of sight" system to be implemented, we could to for now with considering the LOS and PATHs variables as data which get fed into the statsblock from an external system
# Invisible requires los
# Petrified also interact with a sensory system 
# Prone requires a distance system for the advantage check
# Stunned requires thinking about the "speak action"
# Unconscious is a wrapper and requires dropping weapons (where?) 
# Hidden requires a "stealth" system to be implemented which requires sensory system
#Doable:
# Paralyzed induces the Incapacted effect so we need to reason a bit about this nested dependecies
# Restrained we finally have some saving throws to interact with
# Incapacitated
# Poisoned
# Doding
# Dashing
# Helping/Helped

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

# In infinipy/dnd/conditions.py


class Frightened(Condition):
    name: str = "Frightened"
    source_entity_id: str

    def apply(self, stats_block: 'StatsBlock') -> None:
        print(f"Applying Frightened condition to {stats_block.name}")
        
        # Add disadvantage to all attacks
        for action in stats_block.actions:
            if isinstance(action, Attack):
                action.hit_bonus.self_effects.add_disadvantage_condition("Frightened", self.frightened_check)
        
        # Add disadvantage to all skill checks
        for skill in Skills:
            skill_obj = stats_block.skills.get_skill(skill)
            skill_obj.bonus.self_effects.add_disadvantage_condition("Frightened", self.frightened_check)

    def remove(self, stats_block: 'StatsBlock') -> None:
        print(f"Removing Frightened condition from {stats_block.name}")
        
        # Remove disadvantage from all attacks
        for action in stats_block.actions:
            if isinstance(action, Attack):
                action.hit_bonus.self_effects.remove_effect("Frightened")
        
        # Remove disadvantage from all skill checks
        for skill in Skills:
            skill_obj = stats_block.skills.get_skill(skill)
            skill_obj.bonus.self_effects.remove_effect("Frightened")

    @staticmethod
    def frightened_check(source: 'StatsBlock', target: Optional['StatsBlock']) -> bool:
        if "Frightened" in source.active_conditions:
            frightened_condition = source.active_conditions["Frightened"]
            return source.is_in_line_of_sight(frightened_condition.source_entity_id)
        return False


class Grappled(Condition):
    name: str = "Grappled"
    source_entity_id: str

    def apply(self, stats_block: 'StatsBlock') -> None:
        print(f"Applying Grappled condition to {stats_block.name}")
        stats_block.speed.set_speed_to_zero("Grappled")

    def remove(self, stats_block: 'StatsBlock') -> None:
        print(f"Removing Grappled condition from {stats_block.name}")
        stats_block.speed.reset_speed("Grappled")

class Incapacitated(Condition):
    name: str = "Incapacitated"

    def apply(self, stats_block: 'StatsBlock') -> None:
        print(f"Applying Incapacitated condition to {stats_block.name}")
        stats_block.action_economy.modify_actions("Incapacitated", -stats_block.action_economy.actions.base_value)
        stats_block.action_economy.modify_bonus_actions("Incapacitated", -stats_block.action_economy.bonus_actions.base_value)
        stats_block.action_economy.modify_reactions("Incapacitated", -stats_block.action_economy.reactions.base_value)

    def remove(self, stats_block: 'StatsBlock') -> None:
        print(f"Removing Incapacitated condition from {stats_block.name}")
        stats_block.action_economy.remove_actions_modifier("Incapacitated")
        stats_block.action_economy.remove_bonus_actions_modifier("Incapacitated")
        stats_block.action_economy.remove_reactions_modifier("Incapacitated")

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
    def poisoned_check(source: 'StatsBlock', target: Optional['StatsBlock']) -> bool:
        return True  # Always apply disadvantage when poisoned


class Restrained(Condition):
    name: str = "Restrained"

    def apply(self, stats_block: 'StatsBlock') -> None:
        print(f"Applying Restrained condition to {stats_block.name}")
        
        # Set speed to 0
        stats_block.speed.set_speed_to_zero("Restrained")
        
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
        stats_block.speed.reset_speed("Restrained")
        
        # Remove disadvantage from all attacks
        for action in stats_block.actions:
            if isinstance(action, Attack):
                action.hit_bonus.self_effects.remove_effect("Restrained")
        
        # Remove disadvantage from Dexterity saving throws
        dex_save = stats_block.saving_throws.get_ability(Ability.DEX)
        dex_save.bonus.self_effects.remove_effect("Restrained")

    @staticmethod
    def restrained_check(source: 'StatsBlock', target: Optional['StatsBlock']) -> bool:
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
    def dodging_check(source: 'StatsBlock', target: Optional['StatsBlock']) -> bool:
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
    def dashing_check(source: 'StatsBlock', target: Optional['StatsBlock']) -> bool:
        return True  # Always apply the effect when dashing
    
