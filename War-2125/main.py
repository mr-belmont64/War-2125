#!/usr/bin/env python3

import copy
import traceback

import tcod

from actions import StartGameAction
import color
from engine import Engine
from entity import Actor
from input_handler import MainGameEventHandler, MainMenuHandler
from entity_loader import EntityLoader
from components.ai import HostileEnemy
from components.fighter import Fighter
from procgen import generate_wilderness
from setup_game import create_new_game


def main() -> None:
    screen_width = 80
    screen_height = 50

    map_width = 250
    map_height = 250

    max_monsters = 15

    tileset = tcod.tileset.load_tilesheet(
        "dejavu10x10_gs_tc.png", 32, 8, tcod.tileset.CHARMAP_TCOD
    )

    player = Actor(
        x=0,
        y=0,
        char="@",
        color=(255, 255, 255),
        name="Survivor",
        ai_cls=HostileEnemy,
        fighter=Fighter(hp=50, defense=2, power=5),
    )

    engine = Engine(player=player)
    monster_loader = EntityLoader("monsters/zeds.json")

    engine.game_map = generate_wilderness(
        map_width=map_width,
        map_height=map_height,
        max_monsters=max_monsters,
        engine=engine,
        monster_loader=monster_loader,
    )
    engine.update_fov()

    engine.message_log.add_message(
        "Hello, Welcome to the tech demo of War 2125, if you are playing this, what the fuck the game isn't even out yet.", color.welcome_text,
    )

    handler = MainMenuHandler()

    while True:
        with tcod.context.new(
            columns=screen_width,
            rows=screen_height,
            tileset=tileset,
            title="War-2125",
            vsync=True,
        ) as context:
            root_console = tcod.console.Console(screen_width, screen_height, order="F")

            while True:
                root_console.clear()

                handler.on_render(console=root_console)
                context.present(root_console)

                for event in tcod.event.wait():
                    action = handler.dispatch(event)

                    if isinstance(action, StartGameAction):
                        engine = create_new_game()
                        handler = MainGameEventHandler(engine)

    engine.event_handler = MainGameEventHandler(engine)

    with tcod.context.new(
        columns=screen_width,
        rows=screen_height,
        tileset=tileset,
        title="WAR-2136",
        vsync=True,
    ) as context:
        root_console = tcod.console.Console(screen_width, screen_height, order="F")
        while True:
            root_console.clear()
            engine.event_handler.on_render(console=root_console)
            context.present(root_console)

            for event in tcod.event.get():
                context.convert_event(event)  # Maps mouse coordinates to terminal grid tiles
                engine.event_handler.handle_events(event)


if __name__ == "__main__":
    main()