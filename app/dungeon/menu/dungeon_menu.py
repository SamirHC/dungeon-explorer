import pygame

from app.common.action import Action
from app.common.inputstream import InputStream
from app.common import constants, settings
from app.common.menu import MenuController, MenuOption, MenuPage, MenuRenderer
from app.dungeon.menu.move_menu import MoveMenuRenderer
from app.dungeon.menu.stairs_menu import StairsMenu
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
        self.is_active = False
        self.is_message_log_active = False
        self.intent = None

        # Menu
        self.menu = self.build_menu()
        self.menu_controller = MenuController(self.menu)
        self.top_menu_renderer = MenuRenderer((8, 14), alpha=MENU_ALPHA)
        self.move_menu_renderer = MoveMenuRenderer()
        self.leader_move_sub_menu_renderer = MenuRenderer((10, 13), alpha=MENU_ALPHA)
        self.ally_move_sub_menu_renderer = MenuRenderer((10, 11), alpha=MENU_ALPHA)
        self.others_menu_renderer = MenuRenderer(
            (15, 17),
            alpha=MENU_ALPHA,
            header=True,
            footer=True,
            title=text.TextBuilder.build_white("  Others"),
        )
        # Ground
        self.stairs_menu = StairsMenu()

    def build_menu(self):
        top_menu = MenuPage("TopMenu-0")
        top_menu.add_option(moves_option := MenuOption("Moves"))
        top_menu.add_option(MenuOption("Items"))
        top_menu.add_option(MenuOption("Team"))
        top_menu.add_option(others_option := MenuOption("Others"))
        top_menu.add_option(MenuOption("Ground"))
        top_menu.add_option(MenuOption("Rest"))
        top_menu.add_option(MenuOption("Exit"))

        # Moves
        moves_menus = []
        for team_idx, pokemon in enumerate(self.dungeon.party):
            pokemon_move_menu = MenuPage(("Moves", team_idx))

            for moveset_idx, move in enumerate(pokemon.moveset):
                opt = MenuOption(
                    moveset_idx,
                    enabled=pokemon.moveset.can_use(moveset_idx),
                    metadata={"Move Name": move.name}
                )
                pokemon_move_menu.add_option(opt)

                move_sub_menu = MenuPage(("MoveSubMenu", team_idx, moveset_idx))

                if team_idx == 0:  # Leader
                    move_sub_menu.add_option(MenuOption("Use"))
                move_sub_menu.add_option(MenuOption("Switch"))
                move_sub_menu.add_option(MenuOption("Shift Up", enabled=(moveset_idx != 0)))
                move_sub_menu.add_option(MenuOption("Shift Down", enabled=(moveset_idx != len(pokemon.moveset) - 1)))
                move_sub_menu.add_option(MenuOption("Info"))
                move_sub_menu.add_option(MenuOption("Exit"))

                opt.set_child_menu(move_sub_menu)

            moves_menus.append(pokemon_move_menu)

        MenuPage.connect_pages(*moves_menus)
        moves_option.set_child_menu(moves_menus[0])

        # Items
        # Team
        # Others
        others_menu = MenuPage("Others-0-4")
        others_menu.add_option(MenuOption("Options"))
        others_menu.add_option(MenuOption("Window"))
        others_menu.add_option(MenuOption("Map"))
        others_menu.add_option(MenuOption("Message log"))
        others_menu.add_option(MenuOption("Mission objectives"))
        others_menu.add_option(MenuOption("Dungeon hints"))

        others_option.set_child_menu(others_menu)
        # Ground
        # Rest

        return top_menu

    def process_input(self, input_stream: InputStream):
        kb = input_stream.keyboard
        if kb.is_pressed(settings.get_key(Action.MENU)):
            self.intent = Action.MENU
        elif kb.is_pressed(settings.get_key(Action.INTERACT)):
            self.intent = Action.INTERACT
        elif kb.is_pressed(settings.get_key(Action.DOWN)):
            self.intent = Action.DOWN
        elif kb.is_pressed(settings.get_key(Action.UP)):
            self.intent = Action.UP
        elif kb.is_pressed(settings.get_key(Action.LEFT)):
            self.intent = Action.LEFT
        elif kb.is_pressed(settings.get_key(Action.RIGHT)):
            self.intent = Action.RIGHT

    def update(self):
        intent, self.intent = self.intent, None

        if not self.is_active:
            match intent:
                case Action.MENU:
                    self.is_active = True
            return

        assert self.is_active

        if self.is_message_log_active:
            match intent:
                case Action.UP:
                    self.message_log.scroll_up()
                case Action.DOWN:
                    self.message_log.scroll_down()
                case Action.MENU:
                    self.is_message_log_active = False
            return

        self.top_menu_renderer.update()

        match intent:
            case Action.MENU if self.menu_controller.current_page.label == "TopMenu-0":
                if self.menu.current_option.label == "Exit":
                    self.menu.pointer = 0
                self.is_active = False
            case Action.MENU:
                self.menu_controller.back()
            case Action.INTERACT:
                self.top_menu_renderer.pointer_animation.restart()
                self.menu_controller.select()
            case Action.DOWN:
                self.top_menu_renderer.pointer_animation.restart()
                self.menu_controller.next()
            case Action.UP:
                self.top_menu_renderer.pointer_animation.restart()
                self.menu_controller.prev()
            case Action.LEFT:
                self.top_menu_renderer.pointer_animation.restart()
                self.menu_controller.prev_page()
            case Action.RIGHT:
                self.top_menu_renderer.pointer_animation.restart()
                self.menu_controller.next_page()

        menu_intent = self.menu_controller.consume_intent()
        match menu_intent:
            # Move intents:
            case "Use":
                move_menu = self.menu_controller.current_page.parent_menu
                move_idx = move_menu.current_option.label
                self.battle_system.attacker = self.dungeon.party.leader
                self.battle_system.activate(move_idx)
                self.menu_controller.back()
                self.menu_controller.back()
                self.is_active = False
            case "Switch":
                move_menu = self.menu_controller.current_page.parent_menu
                _, team_idx = move_menu.label
                move_idx = move_menu.current_option.label
                self.dungeon.party[team_idx].moveset.switch(move_idx)
            case "Shift Up":
                move_menu = self.menu_controller.current_page.parent_menu
                _, team_idx = move_menu.label
                move_idx = move_menu.current_option.label
                move_menu.pointer = self.dungeon.party[team_idx].moveset.shift_up(move_idx)
                self.menu_controller.current_page.pointer = 0
                self.menu_controller.back()
            case "Shift Down":
                move_menu = self.menu_controller.current_page.parent_menu
                _, team_idx = move_menu.label
                move_idx = move_menu.current_option.label
                move_menu.pointer = self.dungeon.party[team_idx].moveset.shift_down(move_idx)
                self.menu_controller.current_page.pointer = 0
                self.menu_controller.back()
            case "Info":
                print("Info not implemented")
                self.menu_controller.current_page.pointer = 0
                self.menu_controller.back()
            case "Exit" if self.menu_controller.current_page.label[0] == "MoveSubMenu":
                self.menu_controller.current_page.pointer = 0
                self.menu_controller.back()
            # Others Menu Intents:
            case "Message log":
                self.is_message_log_active = True
            # Top Menu Intents:
            case "Items":
                print("Items not implemented")
            case "Team":
                for p in self.dungeon.party:
                    print(p.base.name, p.status.hp.value)                
            case "Ground":
                print("Ground not fully implemented")
                # if self.dungeon.floor.user_at_stairs():
                #    self.current_menu = self.stairs_menu
            case "Rest":
                print("Rest not implemented")
            case "Exit" if self.menu_controller.current_page.label == "TopMenu-0":
                self.menu.pointer = 0
                self.is_active = False
            case x if x is not None:
                print(x)

    def render(self) -> pygame.Surface:
        surface = pygame.Surface(constants.DISPLAY_SIZE, pygame.SRCALPHA)

        if not self.is_active:
            return surface
    
        if self.is_message_log_active:
            surface.blit(self.message_log.render(), (8, 8))
            return surface

        match self.menu_controller.current_page.label:
            case "TopMenu-0":
                surface.blit(self.top_menu_renderer.render(self.menu), (8, 8))
                surface.blit(self.get_title_surface(), (80, 24))
                surface.blit(self.get_party_status_surface(), (8, 120))
            case ("Moves", team_idx):
                move_menu_surface = self.move_menu_renderer.render(
                    target_pokemon=self.dungeon.party[team_idx],
                    page=team_idx,
                    num_pages=len(self.dungeon.party),
                    menu=self.menu_controller.current_page
                )
                surface.blit(move_menu_surface,(0, 0))
            case ("MoveSubMenu", team_idx, _):
                move_menu_surface = self.move_menu_renderer.render(
                    target_pokemon=self.dungeon.party[team_idx],
                    page=team_idx,
                    num_pages=len(self.dungeon.party),
                    menu=self.menu_controller.current_page.parent_menu,
                    static_pointer=True,
                )
                surface.blit(move_menu_surface,(0, 0))
                if team_idx == 0:
                    move_sub_menu_surface = self.leader_move_sub_menu_renderer.render(self.menu_controller.current_page)
                else:
                    move_sub_menu_surface = self.ally_move_sub_menu_renderer.render(self.menu_controller.current_page)
                surface.blit(move_sub_menu_surface, (168, 8))
            case "Others-0-4":
                others_menu_surface = self.others_menu_renderer.render(self.menu_controller.current_page)
                surface.blit(others_menu_surface, (8, 8))

        return surface

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




"""
    # Creates new MoveMenu to account for changing party state, i.e. when partner faints
    def get_moves_menu(self):
        self.moves_menu = MoveMenu(self.dungeon.party, self.battle_system)
        return self.moves_menu

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
                case "Rest":
                    print("Rest not implemented")
                case "Exit":
                    self.top_menu.pointer = 0
                    self.current_menu = None

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
                    self.stairs_menu.menu.pointer = 0
                    if self.stairs_menu.is_quick_access:
                        self.stairs_menu.is_quick_access = False
                        self.current_menu = None
                    else:
                        self.current_menu = self.top_menu
        elif kb.is_pressed(settings.get_key(Action.MENU)):
            if self.stairs_menu.is_quick_access:
                self.stairs_menu.is_quick_access = False
                self.current_menu = None
            else:
                self.current_menu = self.top_menu
"""
