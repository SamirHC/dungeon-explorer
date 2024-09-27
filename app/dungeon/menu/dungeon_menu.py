import pygame

from app.common.action import Action
from app.common.inputstream import InputStream
from app.common import menu, constants, settings
from app.dungeon.menu.move_menu import MoveMenu
from app.dungeon.menu.stairs_menu import StairsMenu
from app.dungeon.menu.others_menu import OthersMenu
from app.dungeon.battle_system import BattleSystem
from app.dungeon.dungeon import Dungeon
from app.gui.frame import Frame
import app.db.font as font_db
from app.gui import text
from app.gui.textbox import DungeonMessageLog


MENU_ALPHA = 128


class DungeonMenu:
    def __init__(
        self,
        dungeon: Dungeon,
        battle_system: BattleSystem,
        message_log: DungeonMessageLog,
    ):
        self.dungeon = dungeon
        self.battle_system = battle_system
        self.message_log = message_log
        self.current_menu = None

        # Top Menu
        self.top_menu = menu.Menu(
            (8, 14),
            ["Moves", "Items", "Team", "Others", "Ground", "Rest", "Exit"],
            MENU_ALPHA,
        )
        # Moves
        self.moves_menu = MoveMenu(self.dungeon.party, self.battle_system)
        # Others
        self.others_menu = OthersMenu(message_log)
        # Ground
        self.stairs_menu = StairsMenu()

    # Creates new MoveMenu to account for changing party state, i.e. when partner faints
    def get_moves_menu(self):
        self.moves_menu = MoveMenu(self.dungeon.party, self.battle_system)
        return self.moves_menu

    def process_input(self, input_stream: InputStream):
        match self.current_menu:
            case None:
                self.process_input_no_menu(input_stream)
            case self.top_menu:
                self.process_input_top_menu(input_stream)
            case self.moves_menu:
                self.process_input_moves_menu(input_stream)
            case self.others_menu:
                self.process_input_others_menu(input_stream)
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
                    self.current_menu = self.get_moves_menu()
                case "Items":
                    print("Items not implemented")
                case "Team":
                    for p in self.dungeon.party:
                        print(p.base.name, p.status.hp.value)
                case "Others":
                    self.current_menu = self.others_menu
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

    def process_input_others_menu(self, input_stream: InputStream):
        kb = input_stream.keyboard
        if self.others_menu.status == "Top" and kb.is_pressed(
            settings.get_key(Action.MENU)
        ):
            self.current_menu = self.top_menu
        self.others_menu.process_input(input_stream)

    def process_input_stairs_menu(self, input_stream: InputStream):
        self.stairs_menu.process_input(input_stream)
        kb = input_stream.keyboard
        if kb.is_pressed(settings.get_key(Action.INTERACT)):
            match self.stairs_menu.menu.current_option:
                case "Proceed":
                    self.stairs_menu.proceed = True
                case "Info":
                    print(
                        "Stairs leading to the next floor. If you are on\n"
                        "the final floor, you will escape from the\n"
                        "dungeon."
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
                self.top_menu.update()
            case self.moves_menu:
                if self.moves_menu.is_move_used:
                    self.moves_menu.is_move_used = False
                    self.current_menu = None
                self.moves_menu.update()
            case self.others_menu:
                self.others_menu.update()
            case self.stairs_menu:
                self.stairs_menu.update()

    def render(self) -> pygame.Surface:
        self.surface = pygame.Surface(constants.DISPLAY_SIZE, pygame.SRCALPHA)
        match self.current_menu:
            case self.top_menu:
                return self.render_top_menu()
            case self.moves_menu:
                return self.moves_menu.render()
            case self.others_menu:
                return self.others_menu.render()
            case self.stairs_menu:
                return self.stairs_menu.render()
            case _:
                return self.surface

    def render_top_menu(self) -> pygame.Surface:
        self.surface.blit(self.top_menu.render(), (8, 8))
        self.surface.blit(self.get_title_surface(), (80, 24))
        self.surface.blit(self.get_party_status_surface(), (8, 120))
        return self.surface

    def get_title_surface(self) -> pygame.Surface:
        title = text.TextBuilder.build_color(
            text.BROWN, self.dungeon.dungeon_data.name
        ).render()

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
            name_surf = text.TextBuilder.build_color(
                p.name_color, f" {p.base.name}"
            ).render()
            frame_surface.blit(name_surf, start)
            start += row_space
            hp_surf = text.TextBuilder.build_white(
                f"{p.status.hp.value: >3}/{p.stats.hp.value: >3}"
            ).render()
            hp_rect = hp_surf.get_rect(topright=end)
            frame_surface.blit(hp_surf, hp_rect.topleft)
            end += row_space
        # Render leader belly
        name_start = pygame.Vector2(frame_surface.container_rect.centerx + 3, 8)
        val_start = pygame.Vector2(168, 8)
        belly_name_surf = text.TextBuilder.build_white("Belly:").render()
        belly = self.dungeon.party.leader.status.belly
        belly_val_surf = text.TextBuilder.build_white(
            f"{belly.value}/{belly.max_value}"
        ).render()
        frame_surface.blit(belly_name_surf, name_start)
        frame_surface.blit(belly_val_surf, val_start)
        name_start += row_space
        val_start += row_space
        # Render money
        money_name_surf = text.TextBuilder.build_white("Money:").render()
        money_val_surf = (
            text.TextBuilder()
            .set_shadow(True)
            .set_color(text.CYAN)
            .write(f"{self.dungeon.inventory.money:,}".replace(",", ", "))
            .set_font(font_db.graphic_font)
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
        weather_name_surf = text.TextBuilder.build_white("Weather:").render()
        weather_val_surf = text.TextBuilder.build_white(
            f"{self.dungeon.floor.status.weather.name.capitalize()}"
        ).render()
        frame_surface.blit(weather_name_surf, name_start)
        frame_surface.blit(weather_val_surf, val_start)
        name_start += row_space
        val_start += row_space
        # Render time
        play_time_name_surf = text.TextBuilder.build_white("Play:").render()
        play_time_val_surf = text.TextBuilder.build_white("0:00:00").render()
        frame_surface.blit(play_time_name_surf, name_start)
        frame_surface.blit(play_time_val_surf, val_start)
        return frame_surface
