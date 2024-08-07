import pygame

from app.common.action import Action
from app.common.inputstream import InputStream
from app.common import menu, constants, settings
from app.dungeon.menu.move_menu import MoveMenu
from app.dungeon.menu.stairs_menu import StairsMenu
from app.dungeon.battle_system import BattleSystem
from app.dungeon.dungeon import Dungeon
from app.gui.frame import Frame
import app.db.database as db
from app.gui import text


MENU_ALPHA = 128


class DungeonMenu:
    def __init__(self, dungeon: Dungeon, battle_system: BattleSystem):
        self.dungeon = dungeon

        # Top Menu
        self.top_menu = menu.Menu(
            (8, 14),
            ["Moves", "Items", "Team", "Others", "Ground", "Rest", "Exit"],
            MENU_ALPHA,
        )
        self.dungeon_title = self.get_title_surface()

        # Moves
        self.moves_menu = MoveMenu(dungeon.party, battle_system)

        # Ground
        self.stairs_menu = StairsMenu()

        self.current_menu = None

    def get_title_surface(self) -> pygame.Surface:
        title = (
            text.TextBuilder()
            .set_shadow(True)
            .set_color(text.BROWN)
            .write(self.dungeon.dungeon_data.name)
            .build()
            .render()
        )
        surface = Frame((21, 4), MENU_ALPHA)
        rect = title.get_rect(center=surface.get_rect().center)
        surface.blit(title, rect.topleft)
        return surface

    def get_party_status_surface(self) -> pygame.Surface:
        frame_surface = Frame((30, 8), MENU_ALPHA)
        row_space = pygame.Vector2(0, 12)
        # Render names/hp
        start = frame_surface.container_rect.topleft
        end = pygame.Vector2(117, 8)
        for p in self.dungeon.party:
            name_surf = (
                text.TextBuilder()
                .set_shadow(True)
                .set_color(p.name_color)
                .write(f" {p.data.name}")
                .build()
                .render()
            )
            frame_surface.blit(name_surf, start)
            start += row_space
            hp_surf = (
                text.TextBuilder()
                .set_shadow(True)
                .set_color(text.WHITE)
                .write(f"{p.status.hp.value: >3}/{p.stats.hp.value: >3}")
                .build()
                .render()
            )
            hp_rect = hp_surf.get_rect(topright=end)
            frame_surface.blit(hp_surf, hp_rect.topleft)
            end += row_space
        # Render leader belly
        name_start = pygame.Vector2(frame_surface.container_rect.centerx + 3, 8)
        val_start = pygame.Vector2(168, 8)
        belly_name_surf = (
            text.TextBuilder()
            .set_shadow(True)
            .set_color(text.WHITE)
            .write("Belly:")
            .build()
            .render()
        )
        belly_val_surf = (
            text.TextBuilder()
            .set_shadow(True)
            .set_color(text.WHITE)
            .write(
                f"{self.dungeon.user.status.belly.value}/{self.dungeon.user.status.belly.max_value}"
            )
            .build()
            .render()
        )
        frame_surface.blit(belly_name_surf, name_start)
        frame_surface.blit(belly_val_surf, val_start)
        name_start += row_space
        val_start += row_space
        # Render money
        money_name_surf = (
            text.TextBuilder()
            .set_shadow(True)
            .set_color(text.WHITE)
            .write("Money:")
            .build()
            .render()
        )
        money_val_surf = (
            text.TextBuilder()
            .set_shadow(True)
            .set_color(text.CYAN)
            .write("0")
            .set_font(db.font_db.graphic_font)
            .set_shadow(False)
            .write([33])
            .build()
            .render()
        )
        frame_surface.blit(money_name_surf, name_start)
        frame_surface.blit(money_val_surf, val_start)
        name_start += row_space
        val_start += row_space
        # Render weather
        weather_name_surf = (
            text.TextBuilder()
            .set_shadow(True)
            .set_color(text.WHITE)
            .write("Weather:")
            .build()
            .render()
        )
        weather_val_surf = (
            text.TextBuilder()
            .set_shadow(True)
            .set_color(text.WHITE)
            .write(f"{self.dungeon.floor.status.weather.name.capitalize()}")
            .build()
            .render()
        )
        frame_surface.blit(weather_name_surf, name_start)
        frame_surface.blit(weather_val_surf, val_start)
        name_start += row_space
        val_start += row_space
        # Render time
        play_time_name_surf = (
            text.TextBuilder()
            .set_shadow(True)
            .set_color(text.WHITE)
            .write("Play:")
            .build()
            .render()
        )
        play_time_val_surf = (
            text.TextBuilder()
            .set_shadow(True)
            .set_color(text.WHITE)
            .write("0:00:00")
            .build()
            .render()
        )
        frame_surface.blit(play_time_name_surf, name_start)
        frame_surface.blit(play_time_val_surf, val_start)
        return frame_surface

    def process_input(self, input_stream: InputStream):
        match self.current_menu:
            case None:
                self.process_input_no_menu(input_stream)
            case self.top_menu:
                self.process_input_top_menu(input_stream)
            case self.moves_menu:
                self.process_input_moves_menu(input_stream)
            case self.stairs_menu:
                self.process_input_stairs_menu(input_stream)

    def process_input_no_menu(self, input_stream: InputStream):
        if input_stream.keyboard.is_pressed(settings.get_key(Action.MENU)):
            self.current_menu = self.top_menu

    def process_input_top_menu(self, input_stream: InputStream):
        self.top_menu.process_input(input_stream)
        kb = input_stream.keyboard
        if kb.is_pressed(settings.get_key(Action.MENU)):
            if self.top_menu.current_option == "Exit":
                self.top_menu.pointer = 0
            self.current_menu = None
        elif kb.is_pressed(settings.get_key(Action.INTERACT)):
            match self.top_menu.current_option:
                case "Moves":
                    self.current_menu = self.moves_menu
                case "Items":
                    print("Items not implemented")
                case "Team":
                    for p in self.dungeon.party:
                        print(p.data.name, p.status.hp.value)
                case "Others":
                    print("Others not implemented")
                case "Ground":
                    # print("Ground not fully implemented")
                    if self.dungeon.floor.user_at_stairs():
                        self.current_menu = self.stairs_menu
                        self.stairs_menu.auto = False
                case "Rest":
                    print("Rest not implemented")
                case "Exit":
                    self.top_menu.pointer = 0
                    self.current_menu = None

    def process_input_moves_menu(self, input_stream: InputStream):
        self.moves_menu.process_input(input_stream)
        if input_stream.keyboard.is_pressed(settings.get_key(Action.MENU)):
            self.moves_menu.is_submenu_active = False
            self.current_menu = self.top_menu

    def process_input_stairs_menu(self, input_stream: InputStream):
        self.stairs_menu.process_input(input_stream)
        kb = input_stream.keyboard
        if kb.is_pressed(settings.get_key(Action.INTERACT)):
            match self.stairs_menu.menu.current_option:
                case "Proceed":
                    self.stairs_menu.proceed = True
                case "Info":
                    print(
                        "Stairs leading to the next floor. If you are on\nthe final floor, you will escape from the\ndungeon."
                    )
                case "Cancel":
                    self.stairs_menu.cancelled = True
                    self.stairs_menu.menu.pointer = 0
                    if self.stairs_menu.auto:
                        self.current_menu = None
                    else:
                        self.current_menu = self.top_menu
        elif kb.is_pressed(settings.get_key(Action.MENU)):
            if self.stairs_menu.auto:
                self.stairs_menu.cancelled = True
                self.current_menu = None
            else:
                self.current_menu = self.top_menu

    def update(self):
        match self.current_menu:
            case self.top_menu:
                self.update_top_menu()
            case self.moves_menu:
                if self.moves_menu.is_move_used:
                    self.moves_menu.is_move_used = False
                    self.current_menu = None
                self.update_moves_menu()
            case self.stairs_menu:
                self.stairs_menu.update()

    def update_top_menu(self):
        self.top_menu.update()

    def update_moves_menu(self):
        self.moves_menu.update()

    def render(self) -> pygame.Surface:
        self.surface = pygame.Surface(constants.DISPLAY_SIZE, pygame.SRCALPHA)
        match self.current_menu:
            case self.top_menu:
                return self.render_top_menu()
            case self.moves_menu:
                return self.render_moves_menu()
            case self.stairs_menu:
                return self.stairs_menu.render()
            case _:
                return self.surface

    def render_top_menu(self) -> pygame.Surface:
        self.surface.blit(self.top_menu.render(), (8, 8))
        self.surface.blit(self.dungeon_title, (80, 24))
        self.surface.blit(self.get_party_status_surface(), (8, 120))
        return self.surface

    def render_moves_menu(self) -> pygame.Surface:
        self.surface.blit(self.moves_menu.render(), (8, 8))
        return self.surface
