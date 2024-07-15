from typing import Dict, Set, List, Tuple, Optional, Union, Any
from pydantic import BaseModel, Field, computed_field
from fractions import Fraction
import uuid
from colorama import Fore, Back, Style
import colorama
from infinipy.dnd.statsblock import StatsBlock
from infinipy.dnd.shadowcast import compute_fov
from infinipy.dnd.dijkstra import dijkstra
from math import sqrt
from collections import defaultdict


colorama.init()

class RegistryHolder:
    _registry: Dict[str, 'RegistryHolder'] = {}
    _types: Set[type] = set()

    @classmethod
    def register(cls, instance: 'RegistryHolder'):
        cls._registry[instance.id] = instance
        cls._types.add(type(instance))

    @classmethod
    def get_instance(cls, instance_id: str):
        return cls._registry.get(instance_id)

    @classmethod
    def all_instances(cls, filter_type=True):
        if filter_type:
            return [instance for instance in cls._registry.values() if isinstance(instance, cls)]
        return list(cls._registry.values())

    @classmethod
    def all_instances_by_type(cls, type: type):
        return [instance for instance in cls._registry.values() if isinstance(instance, type)]

    @classmethod
    def all_types(cls, as_string=True):
        if as_string:
            return [type_name.__name__ for type_name in cls._types]
        return cls._types

class Entity(StatsBlock, RegistryHolder):
    battlemap_id: Optional[str] = None
    line_of_sight: Set[Tuple[int, int]] = Field(default_factory=set)
    
    def __init__(self, **data):
        super().__init__(**data)
        self.register(self)

    @computed_field
    def is_on_battlemap(self) -> bool:
        return self.battlemap_id is not None

    def set_battlemap(self, battlemap_id: str):
        self.battlemap_id = battlemap_id

    def remove_from_battlemap(self):
        self.battlemap_id = None
        self.line_of_sight.clear()

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.register(self)

    @classmethod
    def get_or_create(cls, entity_id: str, **kwargs):
        instance = cls.get_instance(entity_id)
        if instance is None:
            instance = cls(id=entity_id, **kwargs)
        else:
            instance.update(**kwargs)
        return instance

    def is_in_line_of_sight(self, other: 'Entity') -> bool:
        return other.position in self.line_of_sight

    def get_position(self) -> Optional[Tuple[int, int]]:
        if self.battlemap_id:
            battlemap = RegistryHolder.get_instance(self.battlemap_id)
            if battlemap:
                return battlemap.get_entity_position(self.id)
        return None


class BattleMap(BaseModel, RegistryHolder):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    width: int
    height: int
    tiles: Dict[Tuple[int, int], str] = Field(default_factory=dict)
    entities: Dict[str, Tuple[int, int]] = Field(default_factory=dict)
    positions: Dict[Tuple[int, int], Set[str]] = Field(default_factory=lambda: defaultdict(set))

    def __init__(self, **data):
        super().__init__(**data)
        self.register(self)

    def set_tile(self, x: int, y: int, tile_type: str):
        self.tiles[(x, y)] = tile_type

    def get_tile(self, x: int, y: int) -> Optional[str]:
        return self.tiles.get((x, y))

    def is_blocking(self, x: int, y: int) -> bool:
        tile = self.get_tile(x, y)
        return tile == "WALL"

    def print_ascii_map(self, highlight_los: Optional[Set[Tuple[int, int]]] = None) -> str:
        ascii_map = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                char = self.get_tile_char(x, y)
                if highlight_los and (x, y) in highlight_los:
                    char = Back.YELLOW + char + Style.RESET_ALL
                row.append(char)
            ascii_map.append(''.join(row))
        return '\n'.join(ascii_map)

    def visualize_los(self, position: Tuple[int, int]):
        los_tiles = set()

        def mark_visible(x, y):
            los_tiles.add((x, y))

        compute_fov(position, self.is_blocking, mark_visible)
        print(f"Map with line of sight from {position}:")
        print(self.print_ascii_map(highlight_los=los_tiles))

    def get_tile_char(self, x: int, y: int) -> str:
        tile = self.get_tile(x, y)
        if tile == "WALL":
            return '#'
        elif tile == "WATER":
            return '~'
        elif tile == "FLOOR":
            return '.'
        else:
            return ' '

    def compute_line_of_sight(self, entity: Entity) -> Set[Tuple[int, int]]:
        los_tiles = set()

        def mark_visible(x, y):
            los_tiles.add((x, y))

        compute_fov(entity.get_position(), self.is_blocking, mark_visible)
        return los_tiles
    
    def compute_dijkstra(
        self, start: Tuple[int, int], diagonal: bool = True, max_distance: Optional[int] = None
    ) -> Tuple[Dict[Tuple[int, int], int], Dict[Tuple[int, int], List[Tuple[int, int]]]]:
        def is_walkable(x, y):
            return self.get_tile(x, y) == "FLOOR"

        return dijkstra(start, is_walkable, self.width, self.height, diagonal, max_distance)

    def visualize_dijkstra_distances(self, start: Tuple[int, int], diagonal: bool = True, max_distance: Optional[int] = None):
        distances, _ = self.compute_dijkstra(start, diagonal, max_distance)
        
        ascii_map = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                if (x, y) == start:
                    char = '@'
                elif (x, y) in distances:
                    char = str(distances[(x, y)] % 10)
                else:
                    char = Back.RED + 'X' + Style.RESET_ALL
                row.append(char)
            ascii_map.append(''.join(row))
        return '\n'.join(ascii_map)

    def visualize_dijkstra_path(self, start: Tuple[int, int], end: Tuple[int, int], diagonal: bool = True, max_distance: Optional[int] = None):
        _, paths = self.compute_dijkstra(start, diagonal, max_distance)
        
        if end not in paths:
            return "No path found."

        path_set = set(paths[end])
        ascii_map = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                if (x, y) == start:
                    char = '@'
                elif (x, y) == end:
                    char = Back.GREEN + 'E' + Style.RESET_ALL
                elif (x, y) in path_set:
                    char = Back.GREEN + '.' + Style.RESET_ALL
                else:
                    char = self.get_tile_char(x, y)
                row.append(char)
            ascii_map.append(''.join(row))
        return '\n'.join(ascii_map)

    @staticmethod
    def compute_absolute_distance(start: Tuple[int, int], end: Tuple[int, int]) -> float:
        return sqrt((start[0] - end[0]) ** 2 + (start[1] - end[1]) ** 2) * 5  # 5 feet per tile

    def visualize_absolute_distances(self, start: Tuple[int, int]):
        ascii_map = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                distance = self.compute_absolute_distance(start, (x, y))
                if (x, y) == start:
                    char = '@'
                elif distance < 10:
                    char = f'{int(distance):d}'
                elif distance < 100:
                    char = f'{int(distance):02d}'
                else:
                    char = 'XX'
                row.append(char)
            ascii_map.append(''.join(row))
        return '\n'.join(ascii_map)

    def add_entity(self, entity: Entity, position: Tuple[int, int]):
        entity_id = entity.id
        entity.set_battlemap(self.id)
        self.entities[entity_id] = position
        self.positions[position].add(entity_id)
        self.update_entity_los(entity)

    def remove_entity(self, entity: Entity):
        entity_id = entity.id
        position = self.entities.pop(entity_id, None)
        if position:
            self.positions[position].remove(entity_id)
            if not self.positions[position]:
                del self.positions[position]
        entity.remove_from_battlemap()

    def move_entity(self, entity: Entity, new_position: Tuple[int, int]):
        entity_id = entity.id
        old_position = self.entities[entity_id]
        self.positions[old_position].remove(entity_id)
        if not self.positions[old_position]:
            del self.positions[old_position]

        self.entities[entity_id] = new_position
        self.positions[new_position].add(entity_id)
        self.update_entity_los(entity)

    def get_entity_position(self, entity_id: str) -> Optional[Tuple[int, int]]:
        return self.entities.get(entity_id)

    def update_entity_los(self, entity: Entity):
        entity.line_of_sight = self.compute_line_of_sight(entity)

    def __str__(self) -> str:
        return self.print_ascii_map()
