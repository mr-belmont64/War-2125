from __future__ import annotations

from typing import Iterable, Iterator, Optional, TYPE_CHECKING

import numpy as np
from tcod.console import Console

from entity import Actor
import tiles_type

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity


class GameMap:
    def __init__(
        self, engine: Engine, width: int, height: int, entities: Iterable[Entity] = ()
    ):
        self.engine = engine
        self.width, self.height = width, height
        self.entities = set(entities) 
        self.tiles = np.full((width, height), fill_value=tiles_type.wall, order="F")

        self.visible = np.full(
            (width, height), fill_value=False, order="F"
        )
        self.explored = np.full(
            (width, height), fill_value=False, order="F"
        )

    @property
    def actors(self) -> Iterator[Actor]:
        """Iterate over all living actors currently on this map."""
        yield from (
            entity
            for entity in self.entities
            if isinstance(entity, Actor) and entity.is_alive
        )

    def get_blocking_entity_at_location(
        self, location_x: int, location_y: int
    ) -> Optional[Entity]:
        for entity in self.entities:
            if (
                entity.blocks_movement
                and entity.x == location_x
                and entity.y == location_y
            ):
                return entity

        return None

    def get_actor_at_location(self, x: int, y: int) -> Optional[Actor]:
        """Return the living actor at this specific coordinate, or None if it's empty space."""
        for actor in self.actors:
            if actor.x == x and actor.y == y:
                return actor

        return None

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def render(self, console: Console) -> None:

        viewport_width = 80
        viewport_height = 43

        cam_x = max(0, min(self.engine.player.x - viewport_width // 2, self.width - viewport_width))
        cam_y = max(0, min(self.engine.player.y - viewport_height // 2, self.height - viewport_height))


        visible_slice = self.visible[cam_x : cam_x + viewport_width, cam_y : cam_y + viewport_height]
        explored_slice = self.explored[cam_x : cam_x + viewport_width, cam_y : cam_y + viewport_height]
        tiles_slice = self.tiles[cam_x : cam_x + viewport_width, cam_y : cam_y + viewport_height]
    
        console.rgb[0:viewport_width, 0:viewport_height] = np.select(
            condlist=[visible_slice, explored_slice],
            choicelist=[tiles_slice["light"], tiles_slice["dark"]],
            default=tiles_type.SHROUD,
        )

        for entity in self.entities:
            screen_x = entity.x - cam_x
            screen_y = entity.y - cam_y
            if 0 <= screen_x < viewport_width and 0 <= screen_y < viewport_height:
                console.print(x=screen_x, y=screen_y, string=entity.char, fg=entity.color)
        """
        Renders the map.
        If a tile is in 'visible', draw 'light'.
        If it's in 'explored', draw 'dark'.
        Otherwise, draw 'SHROUD'.
        """
        
        console.rgb[0: viewport_width, 0: viewport_height] = np.select(
            condlist=[visible_slice, explored_slice],
            choicelist=[tiles_slice["light"], tiles_slice["dark"]],
            default=tiles_type.SHROUD,
        )

        entities_sorted_for_rendering = sorted(
            self.entities, key=lambda x: x.render_order.value
        )

        for entity in entities_sorted_for_rendering:
            screen_x = entity.x - cam_x
            screen_y = entity.y - cam_y

            if 0 <= screen_x < viewport_width and 0 <= screen_y < viewport_height:
                    if entity is self.engine.player or self.visible[entity.x, entity.y]:
                        console.print(x=screen_x, y=screen_y, string=entity.char, fg=entity.color)