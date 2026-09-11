from __future__ import annotations

import random
from entity_loader import EntityLoader
from typing import Iterator, List, Tuple, TYPE_CHECKING

import tcod
import tcod.noise

from game_map import GameMap
import tiles_type

if TYPE_CHECKING:
    from engine import Engine


class RectangularRoom:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x1 = x
        self.y1 = y
        self.x2 = x + width
        self.y2 = y + height

    @property
    def center(self) -> Tuple[int, int]:
        center_x = int((self.x1 + self.x2) / 2)
        center_y = int((self.y1 + self.y2) / 2)

        return center_x, center_y

    @property
    def inner(self) -> Tuple[slice, slice]:
        """Return the inner area of this room as a 2D array index."""
        return slice(self.x1 + 1, self.x2), slice(self.y1 + 1, self.y2)

    def intersects(self, other: RectangularRoom) -> bool:
        """Return True if this room overlaps with another RectangularRoom."""
        return (
            self.x1 <= other.x2
            and self.x2 >= other.x1
            and self.y1 <= other.y2
            and self.y2 >= other.y1
        )


def place_forest_entities( 
    dungeon: GameMap, 
    maximum_monsters: int,
    monster_loader: EntityLoader,
) -> None:
    number_of_monsters = random.randint(0, maximum_monsters)

    available_monsters = list(monster_loader.data.keys())

    if not available_monsters:
        return

    for _ in range(number_of_monsters):

        x = random.randint(1, dungeon.width - 2)
        y = random.randint(1, dungeon.height - 2)

        if dungeon.tiles["walkable"][x, y] and not any(e.x == x and e.y == y for e in dungeon.entities):
            monster_key = random.choice(available_monsters)
            monster = monster_loader.spawn(monster_key, x, y)
            monster.spawn(dungeon, x, y)
            

def generate_wilderness(
    map_width: int,
    map_height: int,
    max_monsters: int,
    engine: Engine,
    monster_loader: EntityLoader,
) -> GameMap:
    """Noise, Please fucking work"""
    player = engine.player
    dungeon = GameMap(engine, map_width, map_height, entities=[player])

    dungeon.tiles[:] = tiles_type.floor

    noise = tcod.noise.Noise(
        dimensions=2,
        algorithm=tcod.NOISE_SIMPLEX,
        octaves=4,
        hurst=0.5,
    )

    scale = 0.03

    for x in range(map_width):
        for y in range(map_height):
            
            if random.random() < 0.15:
                dungeon.tiles[x, y] = tiles_type.wall

    center_x = map_width // 2
    center_y = map_height // 2

    dungeon.tiles[center_x, center_y] = tiles_type.floor
    player.place(center_x, center_y, dungeon)

    place_forest_entities(dungeon, max_monsters, monster_loader)

    return dungeon