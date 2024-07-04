from pydantic import BaseModel, Field
from typing import Optional, TYPE_CHECKING, Dict, Any, Tuple
import uuid
from infinipy.dnd.core import Duration, DurationType, HEARING_DEPENDENT_ABILITIES, Skills
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
    name: str = "Blinded"

    def apply(self, stats_block: 'StatsBlock') -> None:
        # Add disadvantage to all attacks
        for action in stats_block.actions:
            if isinstance(action, Attack):
                action.hit_bonus.self_effects.add_disadvantage_condition("Blinded", lambda src, tgt: True)
        
        # Give advantage to all attacks against this creature
        stats_block.armor_class.base_ac.target_effects.add_advantage_condition("Blinded", lambda src, tgt: True)

    def remove(self, stats_block: 'StatsBlock') -> None:
        # Remove disadvantage from all attacks
        for action in stats_block.actions:
            if isinstance(action, Attack):
                action.hit_bonus.self_effects.remove_effect("Blinded")
        
        # Remove advantage from all attacks against this creature
        stats_block.armor_class.base_ac.target_effects.remove_effect("Blinded")







class Charmed(Condition):
    name: str = "Charmed"
    source_entity_id: str

    def apply(self, stats_block: 'StatsBlock') -> None:
        # Prevent attacking the charmer
        for action in stats_block.actions:
            if isinstance(action, Attack):
                action.contextual_conditions["Charmed"] = self.charmed_attack_check

        # Give advantage on social checks to the charmer
        social_skills = [Skills.DECEPTION, Skills.INTIMIDATION, Skills.PERFORMANCE, Skills.PERSUASION]
        for skill in social_skills:
            print(f"appling charmed to {skill}")
            skill_obj = stats_block.skills.get_skill(skill)
            skill_obj.contextual_effects.add_advantage_condition("Charmed", self.charmed_social_check)

        # self.duration.has_advanced = True  # Mark the first round as advanced

    def remove(self, stats_block: 'StatsBlock') -> None:
        # Remove attack restriction
        for action in stats_block.actions:
            if isinstance(action, Attack):
                action.contextual_conditions.pop("Charmed", None)

        # Remove social check advantage
        social_skills = [Skills.DECEPTION, Skills.INTIMIDATION, Skills.PERFORMANCE, Skills.PERSUASION]
        for skill in social_skills:
            stats_block.skills.get_skill(skill).contextual_effects.remove_effect("Charmed")

    @staticmethod
    def charmed_attack_check(stats_block: 'StatsBlock', target:'StatsBlock') -> Tuple[bool, str]:
        print("TRIGGERED ATTACK CHECKKKK")
        source = stats_block
        if target and source and "Charmed" in source.active_conditions and target.id == source.active_conditions["Charmed"].source_entity_id:
            return False, f"Cannot attack {target.name} due to being charmed."
        return True, ""

    @staticmethod
    def charmed_social_check(stats_block: 'StatsBlock', target:'StatsBlock') -> bool:
        print("GAGAGAGANG Checking for Charmed advantage on social checks")
        source = stats_block
        print(f"Source: {source}, Target: {target}")
        if target and isinstance(target, StatsBlock):
            if "Charmed" in target.active_conditions and target.active_conditions["Charmed"].source_entity_id == source.id:
                return True
        return False

# class Deafened(Condition):
#     name: str = "Deafened"

#     def apply(self, stats_block: 'StatsBlock') -> None:
#         for action in stats_block.actions:
#             if isinstance(action, AbilityCheck) and action.ability in HEARING_DEPENDENT_ABILITIES:
#                 action.automatic_fails.add(action.ability)

#     def remove(self, stats_block: 'StatsBlock') -> None:
#         for action in stats_block.actions:
#             if isinstance(action, AbilityCheck) and action.ability in HEARING_DEPENDENT_ABILITIES:
#                 action.automatic_fails.discard(action.ability)

# class Frightened(Condition):
#     name: str = "Frightened"

#     def apply(self, stats_block: 'StatsBlock') -> None:
#         if stats_block.is_in_line_of_sight(self.source_entity_id):
#             for action in stats_block.actions:
#                 if isinstance(action, Attack):
#                     action.contextual_modifiers.add_self_disadvantage("Frightened", lambda src, tgt: True)
#                 if isinstance(action, AbilityCheck):
#                     action.set_disadvantage()

#     def remove(self, stats_block: 'StatsBlock') -> None:
#         for action in stats_block.actions:
#             if isinstance(action, Attack):
#                 action.contextual_modifiers.self_disadvantages = [
#                     condition for condition in action.contextual_modifiers.self_disadvantages 
#                     if condition[0] != "Frightened"
#                 ]
#             if isinstance(action, AbilityCheck):
#                 action.set_advantage()

#     def update(self, stats_block: 'StatsBlock') -> None:
#         if stats_block.is_in_line_of_sight(self.source_entity_id):
#             self.apply(stats_block)
#         else:
#             self.remove(stats_block)


# class Grappled(Condition):
#     name: str = "Grappled"

#     def apply(self, stats_block: 'StatsBlock') -> None:
#         for speed_type in ["walk", "fly", "swim", "burrow", "climb"]:
#             stats_block.speed.modify_speed(speed_type, self.id, -stats_block.speed.get_speed(speed_type))

#     def remove(self, stats_block: 'StatsBlock') -> None:
#         for speed_type in ["walk", "fly", "swim", "burrow", "climb"]:
#             stats_block.speed.remove_speed_modifier(speed_type, self.id)


# class Incapacitated(Condition):
#     name: str = "Incapacitated"

#     def apply(self, stats_block: 'StatsBlock') -> None:
#         stats_block.action_economy.modify_actions(self.id, -stats_block.action_economy.actions.base_value)
#         stats_block.action_economy.modify_reactions(self.id, -stats_block.action_economy.reactions.base_value)

#     def remove(self, stats_block: 'StatsBlock') -> None:
#         stats_block.action_economy.remove_actions_modifier(self.id)
#         stats_block.action_economy.remove_reactions_modifier(self.id)
