from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from enum import Enum, auto

import tcod.event

from actions import (
    Action,
    BumpAction,
    EscapeAction,
    WaitAction,
    StartGameAction
)
import color
import exceptions


if TYPE_CHECKING:
    from engine import Engine

MOVE_KEYS = {
    # Arrow keys
    tcod.event.KeySym.UP: (0, -1),
    tcod.event.KeySym.DOWN: (0, 1),
    tcod.event.KeySym.LEFT: (-1, 0),
    tcod.event.KeySym.RIGHT: (1, 0),
    tcod.event.KeySym.HOME: (-1, -1),
    tcod.event.KeySym.END: (-1, 1),
    tcod.event.KeySym.PAGEUP: (1, -1),
    tcod.event.KeySym.PAGEDOWN: (1, 1),
    # Numpad keys
    tcod.event.KeySym.KP_1: (-1, 1),
    tcod.event.KeySym.KP_2: (0, 1),
    tcod.event.KeySym.KP_3: (1, 1),
    tcod.event.KeySym.KP_4: (-1, 0),
    tcod.event.KeySym.KP_6: (1, 0),
    tcod.event.KeySym.KP_7: (-1, -1),
    tcod.event.KeySym.KP_8: (0, -1),
    tcod.event.KeySym.KP_9: (1, -1),
}

WAIT_KEYS = {
    tcod.event.KeySym.PERIOD,
    tcod.event.KeySym.KP_5,
    tcod.event.KeySym.CLEAR,
}


class EventHandler(tcod.event.EventDispatch[Action]):
    def __init__(self, engine: Engine):
        self.engine = engine

    def handle_events(self, event: tcod.event.Event) -> None:
        action = self.dispatch(event)
        if action is None:
            return
        self.handle_action(action)

    def handle_action(self, action: Optional[Action]) -> bool:
        if action is None: return False

        try: action.perform()
        except exceptions.Impossibale as exc:
            self.engine.message_log.add_message(exc.args[0], color.impossible)
            return False

        self.engine.handle_enemy_turns()

        self.engine.update_fov()
        return True
            
    def ev_mousemotion(self, event: tcod.event.MouseMotion) -> None:
        if self.engine.game_map.in_bounds(event.tile.x, event.tile.y):
            self.engine.mouse_location = event.tile.x, event.tile.y

    def ev_quit(self, event: tcod.event.Quit) -> Optional[Action]:
        raise SystemExit()

    def on_render(self, console: tcod.Console) -> None:
        self.engine.render(console)

    
class MainGameEventHandler(EventHandler):
    

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        action: Optional[Action] = None
        key = event.sym
        player = self.engine.player

        if key in MOVE_KEYS:
            dx, dy = MOVE_KEYS[key]
            action = BumpAction(player, dx, dy)
        elif key in WAIT_KEYS:
            action = WaitAction(player)
        elif key == tcod.event.KeySym.ESCAPE:
            action = EscapeAction(player)
        elif key == tcod.event.K_v:
            self.engine.event_handler = HistoryViewer(self.engine)

        return action


class GameOverEventHandler(EventHandler):
    def ev_keydown(self, event: tcod.event.KeyDown)-> None:
        if event.sym == tcod.event.K_ESCAPE:
            raise SystemExit()

CURSOR_Y_KEYS = {
    tcod.event.KeySym.UP: -1,
    tcod.event.KeySym.DOWN: 1,
    tcod.event.KeySym.PAGEUP: -10,
    tcod.event.KeySym.PAGEDOWN: 10,
}


class HistoryViewer(EventHandler):
    def __init__(self, engine: Engine):
        super().__init__(engine)
        self.log_length = len(engine.message_log.messages)
        self.cursor = self.log_length - 1

    def on_render(self, console: tcod.Console) -> None:
        super().on_render(console)

        log_console = tcod.Console(console.width - 6, console.height - 6)

        log_console.draw_frame(0, 0, log_console.width, log_console.height)
        log_console.print_box(
            0, 0, log_console.width, 1, "-|Message history|-", alignment=tcod.CENTER
        )

        self.engine.message_log.render_messages(
            log_console,
            1,
            1,
            log_console.width - 2,
            log_console.height - 2,
            self.engine.message_log.messages[: self.cursor + 1],
        )
        log_console.blit(console, 3, 3)

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        if event.sym in CURSOR_Y_KEYS:
            adjust = CURSOR_Y_KEYS[event.sym]
            if adjust < 0 and self.cursor == 0:
                self.cursor = self.log_length - 1
            elif adjust > 0 and self.cursor == self.log_length - 1:
                self.cursor = 0
            else:
                self.cursor = max(0, min(self.cursor + adjust, self.log_length - 1))
        elif event.sym == tcod.event.KeySym.ESCAPE:
            self.engine.event_handler = MainGameEventHandler(self.engine)

class MainMenuHandler(tcod.event.EventDispatch[Action]):

        def on_render(self, console: tcod.console.Console) -> None:
            console.clear()

            console.print(
                console.width // 2,
                console.height // 2 - 4,
                "WAR: 2125",
                fg=(255, 255, 255),
                alignment=tcod.constants.CENTER,
            )
            console.print(
                console.width // 2,
                console.height // 2 - 3,
                "--------------------",
                fg=(100, 100, 100),
                alignment=tcod.constants.CENTER,
            )

            menu_options = [
                "[N]ew Game",
                "[L]oad Game",
                "[S]ettings (WIP)"
                "[T]utoiral (WIP)"
                "[Q]uit"
            ]

            menu_start_y = console.height // 2
            for i, option in enumerate(menu_options):
                console.print(
                    console.width // 2,
                    menu_start_y + (i * 2),
                    option,
                    fg=(200, 200, 200),
                    alignment=tcod.constants.CENTER,

                )
        def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
            key = event.sym

            if key == tcod.event.KeySym.n:
                return StartGameAction()
            elif key == tcod.event.KeySym.q:
                raise SystemExit()
            
class CharacterCreationHandler(tcod.event.EventDispatch[Action]):
            def __int__(self):
                self.points_left = 6
                self.stats = {"STR": 8, "PER": 8, "INT": 8, "DEX": 8}
                self.selected_index = 0
                self.stats_keys = ["STR", "PER", "INT", "DEX"]

            def on_render(self, console: tcod.console.Console) -> None:
                console.clear()

                console.print(
                    console.width // 2,
                    4,
                    "STATS - SPID"
                    fg=(255, 255, 255),
                    alignment=tcod.constants.CENTER,
                )

                start_y = 10
                for i, key in enumerate(self.stat_keys):
                    is_selected = i == self.selected_index
                    prefix -= ">" if is_selected else " "
                    color = (255, 255, 0) if is_selected else (200, 200, 200)

            return None
