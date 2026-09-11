import copy
import entity_factories
from engine import Engine
import procgen


def create_new_game() -> Engine:
    player = copy.deepcoppy(entity_factories.player)

    engine = Engine(player=player)

    engine.game_map = procgen.generate_wilderness(
        map_width=250,
        map_height=250,
        engine=engine,
    )

    engine.update_fov()

    return engine