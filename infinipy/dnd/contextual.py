from pydantic import BaseModel, Field
from typing import Dict, Any, Callable, List, Tuple, TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    from infinipy.dnd.statsblock import StatsBlock


class AdvantageStatus(str, Enum):
    NONE = "None"
    ADVANTAGE = "Advantage"
    DISADVANTAGE = "Disadvantage"

class AdvantageTracker(BaseModel):
    counter: int = 0

    def add_advantage(self, stats_block: 'StatsBlock'):
        if 'Advantage' not in stats_block.modifier_immunity:
            self.counter += 1

    def add_disadvantage(self, stats_block: 'StatsBlock'):
        if 'Disadvantage' not in stats_block.modifier_immunity:
            self.counter -= 1

    def reset(self):
        self.counter = 0

    @property
    def status(self) -> AdvantageStatus:
        if self.counter > 0:
            return AdvantageStatus.ADVANTAGE
        elif self.counter < 0:
            return AdvantageStatus.DISADVANTAGE
        else:
            return AdvantageStatus.NONE

class ContextualEffects(BaseModel):
    bonuses: List[Tuple[str, Callable[['StatsBlock', Any], int]]] = Field(default_factory=list)
    advantage_conditions: List[Tuple[str, Callable[['StatsBlock', Any], bool]]] = Field(default_factory=list)
    disadvantage_conditions: List[Tuple[str, Callable[['StatsBlock', Any], bool]]] = Field(default_factory=list)

    def add_bonus(self, source: str, bonus: Callable[['StatsBlock', Any], int]):
        self.bonuses.append((source, bonus))

    def add_advantage_condition(self, source: str, condition: Callable[['StatsBlock', Any], bool]):
        self.advantage_conditions.append((source, condition))

    def add_disadvantage_condition(self, source: str, condition: Callable[['StatsBlock', Any], bool]):
        self.disadvantage_conditions.append((source, condition))

    def compute_bonus(self, stats_block: 'StatsBlock', target:'StatsBlock') -> int:
        return sum(bonus(stats_block, target) for _, bonus in self.bonuses)

    def has_advantage(self, stats_block: 'StatsBlock', target:'StatsBlock') -> bool:
        print("Advantage Conditions:")
        [print(condition.name) for condition in self.advantage_conditions]
        return any(condition(stats_block, target) for _, condition in self.advantage_conditions)

    def has_disadvantage(self, stats_block: 'StatsBlock', target:'StatsBlock') -> bool:
        return any(condition(stats_block, target) for _, condition in self.disadvantage_conditions)

    def apply_advantage_disadvantage(self, stats_block: 'StatsBlock', target:'StatsBlock', tracker: AdvantageTracker):
        if self.has_advantage(stats_block, target):
            tracker.add_advantage(stats_block)
        if self.has_disadvantage(stats_block, target):
            tracker.add_disadvantage(stats_block)

    def remove_effect(self, source: str):
        self.bonuses = [b for b in self.bonuses if b[0] != source]
        self.advantage_conditions = [a for a in self.advantage_conditions if a[0] != source]
        self.disadvantage_conditions = [d for d in self.disadvantage_conditions if d[0] != source]

class ModifiableValue(BaseModel):
    base_value: int
    static_modifiers: Dict[str, int] = Field(default_factory=dict)
    self_effects: ContextualEffects = Field(default_factory=ContextualEffects)
    target_effects: ContextualEffects = Field(default_factory=ContextualEffects)
    advantage_tracker: AdvantageTracker = Field(default_factory=AdvantageTracker)

    def get_value(self, stats_block: 'StatsBlock', target: Any = None) -> int:
        total = self.base_value + sum(self.static_modifiers.values())
        total += self.self_effects.compute_bonus(stats_block, target)
        if target:
            total += self.target_effects.compute_bonus(target, stats_block)
        return max(0, total)

    def add_static_modifier(self, source: str, value: int):
        self.static_modifiers[source] = value

    def remove_static_modifier(self, source: str):
        self.static_modifiers.pop(source, None)

    def get_advantage_status(self, stats_block: 'StatsBlock', target: 'StatsBlock' = None) -> AdvantageStatus:
        self.advantage_tracker.reset()
        self.self_effects.apply_advantage_disadvantage(stats_block, target, self.advantage_tracker)
        if target:
            self.target_effects.apply_advantage_disadvantage(target, stats_block, self.advantage_tracker)
        return self.advantage_tracker.status