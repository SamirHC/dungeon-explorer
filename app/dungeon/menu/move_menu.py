from app.common import constants, menu, settings
from app.common.action import Action
from app.common.inputstream import InputStream
import app.db.database as db
from app.dungeon.battle_system import BattleSystem
from app.gui.frame import Frame
from app.gui import text
from app.move.move import Move
from app.move.moveset import Moveset
from app.pokemon.party import Party
from app.pokemon.pokemon import Pokemon

import pygame


MENU_ALPHA = 128


class MoveMenu:
    def __init__(self, party: Party, battle_system: BattleSystem):
        self.party = party
        self.battle_system = battle_system
        self.frame = (
            Frame((20, 14), MENU_ALPHA).with_header_divider().with_footer_divider()
        )
        self.menu = menu.PagedMenuModel(
            [[m.name for m in p.moveset] for p in self.party]
        )
        self.leader_submenu = menu.Menu(
            (10, 13),
            ["Use", "Switch", "Shift Up", "Shift Down", "Info", "Exit"],
            MENU_ALPHA,
        )
        self.team_submenu = menu.Menu(
            (10, 11),
            ["Switch", "Shift Up", "Shift Down", "Info", "Exit"],
            MENU_ALPHA,
        )
        self.is_submenu_active = False
        self.is_move_used = False

    @property
    def page(self) -> int:
        return self.menu.page

    @property
    def pointer(self) -> int:
        return self.menu.pointer

    @property
    def target_pokemon(self) -> Pokemon:
        return self.party[self.menu.page]

    @property
    def target_moveset(self) -> Moveset:
        return self.target_pokemon.moveset

    @property
    def target_move(self) -> Move:
        return self.target_moveset[self.pointer]

    @property
    def display_page(self) -> int:
        return self.menu.page + 1

    @property
    def submenu(self) -> menu.Menu:
        return self.leader_submenu if self.page == 0 else self.team_submenu

    def switch(self):
        self.target_moveset.switch(self.pointer)

    def shift_up(self):
        self.menu.pointer = self.target_moveset.shift_up(self.pointer)

    def shift_down(self):
        self.menu.pointer = self.target_moveset.shift_down(self.pointer)

    def process_input(self, input_stream: InputStream):
        if self.is_submenu_active:
            self.process_input_submenu(input_stream)
        else:
            self.process_input_menu(input_stream)

    def process_input_menu(self, input_stream: InputStream):
        kb = input_stream.keyboard
        if kb.is_pressed(settings.get_key(Action.DOWN)):
            db.pointer_animation.restart()
            self.menu.next()
        elif kb.is_pressed(settings.get_key(Action.UP)):
            db.pointer_animation.restart()
            self.menu.prev()
        elif kb.is_pressed(settings.get_key(Action.RIGHT)):
            db.pointer_animation.restart()
            self.menu.next_page()
        elif kb.is_pressed(settings.get_key(Action.LEFT)):
            db.pointer_animation.restart()
            self.menu.prev_page()
        elif kb.is_pressed(settings.get_key(Action.INTERACT)):
            self.is_submenu_active = True
            db.pointer_animation.restart()

    def process_input_submenu(self, input_stream: InputStream):
        self.submenu.process_input(input_stream)
        if not self.submenu.is_active_option:
            return
        if input_stream.keyboard.is_pressed(settings.get_key(Action.INTERACT)):
            match self.submenu.current_option:
                case "Use":
                    self.battle_system.attacker = self.party.leader
                    self.battle_system.activate(self.menu.pointer)
                    self.is_move_used = True
                case "Switch":
                    self.switch()
                case "Shift Up":
                    self.shift_up()
                case "Shift Down":
                    self.shift_down()
                case "Info":
                    print("Info not implemented")
            self.submenu.pointer = 0
            self.is_submenu_active = False
            db.pointer_animation.restart()

    def update(self):
        db.pointer_animation.update()
        if not self.is_submenu_active:
            return
        if self.submenu is self.leader_submenu:
            self.submenu.active[0] = self.target_moveset.can_use(self.pointer)
            self.submenu.active[2] = self.pointer != 0
            self.submenu.active[3] = self.pointer != len(self.target_moveset) - 1
        elif self.submenu is self.team_submenu:
            self.submenu.active[1] = self.pointer != 0
            self.submenu.active[2] = self.pointer != len(self.target_moveset) - 1

    def render(self) -> pygame.Surface:
        surface = pygame.Surface(constants.DISPLAY_SIZE, pygame.SRCALPHA)
        self.render_menu_surface()
        if not self.is_submenu_active:
            surface.blit(self.menu_surface, (8, 8))
            return surface
        self.render_submenu()
        surface.blit(self.render_combined_surface(), (8, 8))
        return surface

    def render_combined_surface(self):
        combined_width = self.frame.get_width() + self.submenu.textbox_frame.get_width()
        combined_height = self.frame.get_height()
        combined_surface = pygame.Surface(
            (combined_width, combined_height), pygame.SRCALPHA
        )
        combined_surface.blit(self.menu_surface, (0, 0))
        combined_surface.blit(self.submenu_surface, (160, 0))
        return combined_surface

    def render_menu_surface(self):
        self.menu_surface = pygame.Surface(self.frame.get_size(), pygame.SRCALPHA)
        self.render_frame()
        self.render_title()
        self.render_page_num()
        self.render_move_dividers()
        self.render_move_name_pp()
        self.render_pointer()
        return self.menu_surface

    def render_frame(self):
        self.menu_surface.blit(self.frame, (0, 0))

    def render_title(self):
        title = (
            text.TextBuilder()
            .set_shadow(True)
            .set_color(self.target_pokemon.name_color)
            .write(f"  {self.target_pokemon.data.name}")
            .set_color(text.WHITE)
            .write("'s moves")
            .build()
            .render()
        )
        self.menu_surface.blit(title, self.frame.container_rect.topleft)

    def render_page_num(self):
        end = pygame.Vector2(self.menu_surface.get_width() - 8, 8)
        page_num_surface = text.TextBuilder.build_white(
            f"({self.display_page}/{len(self.party)})"
        ).render()
        page_num_rect = page_num_surface.get_rect(topright=end)
        self.menu_surface.blit(page_num_surface, page_num_rect.topleft)

    def render_move_dividers(self):
        start = pygame.Vector2(16, 16) + pygame.Vector2(8, 8)
        move_divider = text.divider(127)
        num_move_dividers = len(self.target_moveset) - 1
        for i in range(num_move_dividers):
            start += pygame.Vector2(0, 16)
            self.menu_surface.blit(move_divider, start)

    def render_move_name_pp(self):
        start = pygame.Vector2(8, 18) + self.frame.container_rect.topleft
        end = pygame.Vector2(-4, 18) + self.frame.container_rect.topright
        for i in range(len(self.target_moveset)):
            move = self.target_moveset[i]
            pp_left = self.target_moveset.pp[i]
            if self.target_moveset.selected[i]:
                graphic = 35
            else:
                graphic = 34
            color = text.LIME if pp_left else text.RED
            move_name_surface = (
                text.TextBuilder()
                .set_font(db.font_db.graphic_font)
                .write([graphic])
                .set_font(db.font_db.normal_font)
                .set_shadow(True)
                .set_color(color)
                .write(move.name)
                .build()
                .render()
            )
            self.menu_surface.blit(move_name_surface, start)
            start += pygame.Vector2(0, 16)

            pp_surface = text.TextBuilder.build_color(color, f"{pp_left}/{move.pp}").render()
            pp_rect = pp_surface.get_rect(topright=end)
            self.menu_surface.blit(pp_surface, pp_rect.topleft)
            end += pygame.Vector2(0, 16)

    def render_pointer(self):
        if self.is_submenu_active:
            surf = db.pointer_surface
        else:
            surf = db.pointer_animation.get_current_frame()
        pointer_position = (
            pygame.Vector2(self.frame.container_rect.topleft)
            + pygame.Vector2(0, 18)
            + pygame.Vector2(0, 16) * self.menu.pointer
        )
        self.menu_surface.blit(surf, pointer_position)

    def render_submenu(self):
        self.submenu_surface = self.submenu.render()
