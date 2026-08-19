from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity


class BaseComponent:
    parent: Entity  

    def __init__(self, entity: Entity):
        self.parent = entity

    @property
    def entity(self) -> Entity:
        return self.parent

    @property
    def engine(self) -> Optional[Engine]:
        return self.parent.gamemap.engine if self.parent.gamemap else None