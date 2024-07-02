from typing import Dict, Tuple, List, Optional, Set
from uuid import UUID, uuid4
import copy
from infinipy.dnd.statsblock import StatsBlock
from pydantic import BaseModel, Field

class BattleMap(BaseModel):
    width: int
    height: int
    creature_positions: Dict[UUID, Tuple[int, int]] = Field(default_factory=dict)
    position_creatures: Dict[Tuple[int, int], UUID] = Field(default_factory=dict)

    def place_creature(self, creature_id: UUID, position: Tuple[int, int]):
        if not (0 <= position[0] < self.width and 0 <= position[1] < self.height):
            raise ValueError("Invalid position")
        if position in self.position_creatures:
            raise ValueError("Position already occupied")
        self.creature_positions[creature_id] = position
        self.position_creatures[position] = creature_id

    def remove_creature(self, creature_id: UUID):
        if creature_id in self.creature_positions:
            position = self.creature_positions[creature_id]
            del self.creature_positions[creature_id]
            del self.position_creatures[position]

    def get_creature_position(self, creature_id: UUID) -> Optional[Tuple[int, int]]:
        return self.creature_positions.get(creature_id)

    def get_creature_at_position(self, position: Tuple[int, int]) -> Optional[UUID]:
        return self.position_creatures.get(position)

    def is_adjacent(self, creature1_id: UUID, creature2_id: UUID) -> bool:
        pos1 = self.get_creature_position(creature1_id)
        pos2 = self.get_creature_position(creature2_id)
        if pos1 is None or pos2 is None:
            return False
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1]) == 1
    
    def is_threatened(self, creature_id: str) -> bool:
        creature_pos = self.get_creature_position(creature_id)
        if creature_pos is None:
            return False
        
        for other_id, other_pos in self.creature_positions.items():
            if other_id != creature_id:
                if self.get_distance(creature_pos, other_pos) <= 1:  # Adjacent squares
                    return True
        return False

    def get_all_creatures(self) -> Dict[UUID, Tuple[int, int]]:
        return self.creature_positions.copy()

    def get_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def has_line_of_sight(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> bool:
        # Dummy implementation: always return True for full vision
        return True

    def get_path(self, start: Tuple[int, int], end: Tuple[int, int]) -> List[Tuple[int, int]]:
        # Dummy implementation: return empty list for no movement
        return []

    def get_positions_in_radius(self, center: Tuple[int, int], radius: int) -> List[Tuple[int, int]]:
        positions = []
        for x in range(max(0, center[0] - radius), min(self.width, center[0] + radius + 1)):
            for y in range(max(0, center[1] - radius), min(self.height, center[1] + radius + 1)):
                if self.get_distance(center, (x, y)) <= radius:
                    positions.append((x, y))
        return positions

    def shadowcast(self, center: Tuple[int, int], radius: int) -> Set[Tuple[int, int]]:
        # Dummy implementation: return all positions in radius for full vision
        return set(self.get_positions_in_radius(center, radius))

    def dijkstra(self, start: Tuple[int, int], max_distance: int) -> Dict[Tuple[int, int], int]:
        # Dummy implementation: return empty dict for no movement
        return {}

def create_creature_copy(creature: StatsBlock) -> StatsBlock:
    new_creature = copy.deepcopy(creature)
    new_creature.id = uuid4()  # Assign a new UUID
    return new_creature
