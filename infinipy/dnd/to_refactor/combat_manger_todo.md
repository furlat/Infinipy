### Brainstorming for Combat Manager Enhancements

#### Objective
To improve the D&D 5e simulator's Combat Manager to better capture the variety and complexity of D&D combat, focusing on status tracking, action economy, and applying status effects and consequences of actions.

### Key Areas of Improvement

1. **Status Tracking**
2. **Hit Probability and Consequences**
3. **Action Economy**
4. **SRD 5e Mechanics Integration**

---

### 1. Status Tracking

**Current State:**
- Basic status effects are tracked.
- Limited integration with action outcomes and ongoing conditions.

**Needed Improvements:**
- Comprehensive status effect tracking, including duration, source, and specific conditions.
- Automatic status effect expiration and resolution at appropriate times (e.g., end of turn, start of turn).
- Integration of status effects with action outcomes, modifying hit probabilities and action consequences.

**Detailed List of Status Effects:**
| Status Effect    | Implemented | Description |
|------------------|-------------|-------------|
| Blinded          | No          | Can't see, disadvantage on attack rolls, enemies have advantage. |
| Charmed          | No          | Can't attack the charmer, charmer has advantage on social interactions. |
| Deafened         | No          | Can't hear, disadvantage on sound-based checks. |
| Frightened       | No          | Disadvantage on ability checks and attack rolls while source of fear is in sight. |
| Grappled         | No          | Speed becomes 0, can't benefit from speed bonuses. |
| Incapacitated    | No          | Can't take actions or reactions. |
| Invisible        | No          | Can't be seen, advantage on attack rolls, enemies have disadvantage. |
| Paralyzed        | No          | Incapacitated, can't move or speak, automatic fail Strength and Dexterity saves. |
| Petrified        | No          | Turned into stone, incapacitated, unaware of surroundings. |
| Poisoned         | No          | Disadvantage on attack rolls and ability checks. |
| Prone            | No          | Disadvantage on attack rolls, attackers within 5 feet have advantage. |
| Restrained       | No          | Speed 0, disadvantage on Dexterity saves, attack rolls against have advantage. |
| Stunned          | No          | Incapacitated, can't move, automatic fail Strength and Dexterity saves. |
| Unconscious      | No          | Incapacitated, drops items, automatic fail Strength and Dexterity saves, attack rolls have advantage, hits within 5 feet are critical. |
| Exhaustion       | No          | Multiple levels affecting various attributes. |
| Concentration    | No          | Concentration checks for maintaining spells and effects. |

---

### 2. Hit Probability and Consequences

**Current State:**
- Basic calculation of hit probability and damage.
- Limited application of status effects on hit probability and outcomes.

**Needed Improvements:**
- Modify hit probabilities based on status effects (e.g., blinded, prone).
- Apply damage resistances, immunities, and vulnerabilities.
- Include conditions and saving throws for attack outcomes (e.g., poison, paralysis).

**Detailed Enhancements:**
| Mechanic                       | Implemented | Description |
|--------------------------------|-------------|-------------|
| Advantage/Disadvantage         | Partially   | Modify hit probabilities based on conditions. |
| Resistances and Immunities     | Partially   | Adjust damage calculations based on creature resistances and immunities. |
| Vulnerabilities                | No          | Double damage for vulnerable damage types. |
| Saving Throws                  | No          | Required for many conditions and special attacks. |
| Ongoing Damage                 | No          | Damage effects that persist over multiple turns (e.g., poison, fire). |

---

### 3. Action Economy

**Current State:**
- Basic tracking of actions, bonus actions, and movement.
- Limited support for complex action sequences.

**Needed Improvements:**
- Support for multiple sub-actions within a turn until action economy is exhausted.
- Clear separation and tracking of actions, bonus actions, reactions, and movement.
- Dynamic updates to action economy based on status effects and conditions.

**Detailed Enhancements:**
| Mechanic                  | Implemented | Description |
|---------------------------|-------------|-------------|
| Action Points             | No          | Use action points to allow for multiple sub-actions. |
| Bonus Actions             | Yes         | Allow for specific actions to be taken as a bonus. |
| Reactions                 | Yes         | Track and manage reactions (e.g., opportunity attacks). |
| Movement                  | Yes         | Track and update movement allowance and restrictions. |
| Multiattack               | Partially   | Support for creatures with the Multiattack feature. |

---

### 4. SRD 5e Mechanics Integration

**Current State:**
- Basic combat mechanics and some actions.
- Limited support for SRD 5e detailed rules and conditions.

**Needed Improvements:**
- Full integration of SRD 5e rules for a comprehensive combat experience.
- Detailed tracking and application of all relevant combat mechanics.

**Detailed Enhancements:**
| Mechanic                     | Implemented | Description |
|------------------------------|-------------|-------------|
| Conditions                   | Partially   | Implement all SRD 5e conditions and their effects. |
| Multiattack and Special Abilities | Partially   | Implement creature-specific multiattack and special abilities. |
| Environment Effects          | No          | Integrate environmental effects and terrain advantages. |
| Initiative Modifiers         | Partially   | Consider abilities that modify initiative order. |
| Cover and Concealment        | No          | Implement rules for cover and its impact on hit probabilities. |
| Opportunity Attacks          | Yes         | Track and manage opportunity attacks and triggers. |

---

### Summary of Needed Implementations

| Feature                       | Status      | Notes |
|-------------------------------|-------------|-------|
| Comprehensive Status Tracking | Not Started | Include all SRD 5e conditions, duration, sources, and effects. |
| Hit Probability Modifiers     | Partially   | Implement advantage/disadvantage, resistances, vulnerabilities, and saving throws. |
| Action Economy                | Partially   | Support multiple sub-actions, clear tracking of action types. |
| Full SRD 5e Mechanics         | Partially   | Implement all combat mechanics, including environment effects, cover, and multiattacks. |

### Next Steps
1. **Implement Comprehensive Status Tracking:**
   - Develop data structures to track statuses, durations, and sources.
   - Integrate status effects into action outcomes and hit probability calculations.

2. **Enhance Action Economy:**
   - Implement an action point system or similar mechanism to allow for multiple sub-actions.
   - Ensure dynamic updates to action economy based on statuses and conditions.

3. **Integrate Detailed SRD 5e Mechanics:**
   - Gradually add all remaining SRD 5e mechanics, focusing on high-priority items like saving throws and condition effects.
   - Ensure combat flow and mechanics align with D&D 5e rules for a comprehensive simulation experience.

By addressing these areas, the Combat Manager can be significantly enhanced to provide a more authentic and detailed D&D 5e combat simulation.



### Status Tracking Brainstorming

### Summary Table of Status Effects and Necessary Modifications

Here's an updated table that identifies which components need to be added to the submodels for status effects to properly work. The logic to interact with these components will be contained within the status effect classes themselves.

| **Status Effect**       | **Description**                                                                                             | **Required Components in Submodels**                                                                                        |
|-------------------------|-------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------|
| **Blinded**             | Cannot see, automatically fails any check requiring sight, attack rolls have disadvantage.                  | `Attack`: Add ability to apply disadvantage; `AbilityCheck`: Add failure condition for sight-related checks.                |
| **Charmed**             | Cannot attack the charmer, the charmer has advantage on social interactions.                                | `Attack`: Add logic to prevent attacking charmer; `AbilityCheck`: Add advantage for social interactions with charmer.       |
| **Deafened**            | Cannot hear, automatically fails any check requiring hearing.                                               | `AbilityCheck`: Add failure condition for hearing-related checks.                                                           |
| **Frightened**          | Disadvantage on ability checks and attack rolls while the source of fear is in sight.                       | `Attack`: Add ability to apply disadvantage; `AbilityCheck`: Add ability to apply disadvantage.                              |
| **Grappled**            | Speed becomes 0, can't benefit from any bonus to speed.                                                     | `Speed`: Add logic to set speed to 0.                                                                                       |
| **Incapacitated**       | Cannot take actions or reactions.                                                                           | `ActionEconomy`: Add logic to block actions and reactions.                                                                  |
| **Invisible**           | Impossible to see without special sense, attacks against have disadvantage, attacks have advantage.         | `Attack`: Add ability to apply advantage/disadvantage.                                                                      |
| **Paralyzed**           | Incapacitated, can't move or speak, automatically fails Strength and Dexterity saves, attacks have advantage. | `ActionEconomy`: Add logic to block actions and reactions; `Speed`: Add logic to set speed to 0; `SavingThrow`: Add failure condition. |
| **Petrified**           | Transformed into solid inanimate substance, incapacitated, and unaware of surroundings.                     | `ActionEconomy`: Add logic to block actions and reactions; `Speed`: Add logic to set speed to 0; `SavingThrow`: Add failure condition. |
| **Poisoned**            | Disadvantage on attack rolls and ability checks.                                                            | `Attack`: Add ability to apply disadvantage; `AbilityCheck`: Add ability to apply disadvantage.                              |
| **Prone**               | Disadvantage on attack rolls, attacks within 5 feet have advantage, others have disadvantage.               | `Attack`: Add ability to apply advantage/disadvantage.                                                                      |
| **Restrained**          | Speed becomes 0, attack rolls have disadvantage, Dexterity saves have disadvantage.                         | `Speed`: Add logic to set speed to 0; `Attack`: Add ability to apply disadvantage; `SavingThrow`: Add ability to apply disadvantage. |
| **Stunned**             | Incapacitated, can't move, can speak only falteringly.                                                      | `ActionEconomy`: Add logic to block actions and reactions; `Speed`: Add logic to set speed to 0; `SavingThrow`: Add failure condition. |
| **Unconscious**         | Incapacitated, can't move or speak, unaware of surroundings, drops held items, falls prone.                | `ActionEconomy`: Add logic to block actions and reactions; `Speed`: Add logic to set speed to 0; `SavingThrow`: Add failure condition. |
| **Dodging**             | Attacks against have disadvantage, Dexterity saves have advantage.                                          | `Attack`: Add ability to apply disadvantage; `SavingThrow`: Add ability to apply advantage.                                  |
| **Dashing**             | Movement increases by an additional speed.                                                                  | `Speed`: Add logic to increase movement.                                                                                    |
| **Hiding**              | Makes Dexterity (Stealth) checks to hide.                                                                   | `AbilityCheck`: Add logic for hiding mechanic.                                                                              |
| **Helping**             | Lends aid to another creature, giving advantage on next ability check or attack roll.                       | `Attack`: Add ability to apply advantage; `AbilityCheck`: Add ability to apply advantage.                                   |

### Modifications to Existing Classes

1. **StatsBlock**:
   - Track active status effects with source and id.
   - Methods to apply and remove status effects.

2. **Attack**:
   - Modify hit chance and damage calculations to check for active status effects.
   - Add ability to apply advantage or disadvantage.

3. **SavingThrow**:
   - Modify saving throw calculations to check for active status effects.
   - Add ability to apply advantage or disadvantage.

4. **Speed**:
   - Adjust speed calculations based on active status effects.
   - Add logic to set speed to 0 or increase speed.

5. **ActionEconomy**:
   - Handle incapacitated and similar effects that modify actions and reactions.
   - Add logic to block actions and reactions.

6. **AbilityCheck**:
   - Handle conditions like `charmed` and `poisoned` which affect ability checks.
   - Add ability to apply advantage or disadvantage.

