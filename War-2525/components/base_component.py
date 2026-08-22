from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity
    from game_map import GameMap


class BaseComponent:
    parent: Entity  

    def __init__(self, entity: Entity):
        self.parent = entity

    @property
    def gamemap(self) -> GameMap:
        return self.parent.gamemap

    @property
    def entity(self) -> Entity:
        return self.parent

    @property
    def engine(self) -> Engine:
        return self.gamemap.engine 