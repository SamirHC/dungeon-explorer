import pygame

from app.common import constants
from app.common.menu import MenuPage
import app.db.database as db
from app.gui.frame import Frame
from app.gui import text
from app.pokemon.pokemon import Pokemon
import app.db.font as font_db


MENU_ALPHA = 128


class MoveMenuRenderer:
    def __init__(self):
        self.frame = (
            Frame((20, 14), MENU_ALPHA).with_header_divider().with_footer_divider()
        )
        self.pointer_animation = db.get_pointer_animation()

    def render(self, target_pokemon, page, num_pages, menu: MenuPage, static_pointer=False) -> pygame.Surface:
        surface = pygame.Surface(constants.DISPLAY_SIZE, pygame.SRCALPHA)
        self.render_menu_surface(target_pokemon, page, num_pages)
        self.render_pointer(menu.pointer, static_pointer)
        surface.blit(self.menu_surface, (8, 8))
        return surface

    def render_menu_surface(self, target_pokemon: Pokemon, page, num_pages):
        self.menu_surface = pygame.Surface(self.frame.get_size(), pygame.SRCALPHA)
        self.render_frame()
        self.render_title(target_pokemon)
        self.render_page_num(page, num_pages)
        self.render_move_dividers(target_pokemon)
        self.render_move_name_pp(target_pokemon)
        return self.menu_surface

    def render_frame(self):
        self.menu_surface.blit(self.frame, (0, 0))

    def render_title(self, target_pokemon: Pokemon):
        title = (
            text.TextBuilder()
            .set_shadow(True)
            .set_color(target_pokemon.name_color)
            .write(f"  {target_pokemon.base.name}")
            .set_color(text.WHITE)
            .write("'s moves")
            .build()
            .render()
        )
        self.menu_surface.blit(title, self.frame.container_rect.topleft)

    def render_page_num(self, page, num_pages):
        end = pygame.Vector2(self.menu_surface.get_width() - 8, 8)
        page_num_surface = text.TextBuilder.build_white(
            f"({page}/{num_pages})"
        ).render()
        page_num_rect = page_num_surface.get_rect(topright=end)
        self.menu_surface.blit(page_num_surface, page_num_rect.topleft)

    def render_move_dividers(self, target_pokemon: Pokemon):
        start = pygame.Vector2(16, 16) + pygame.Vector2(8, 8)
        move_divider = text.divider(127)
        num_move_dividers = len(target_pokemon.moveset) - 1
        for i in range(num_move_dividers):
            start += pygame.Vector2(0, 16)
            self.menu_surface.blit(move_divider, start)

    def render_move_name_pp(self, target_pokemon: Pokemon):
        start = pygame.Vector2(8, 18) + self.frame.container_rect.topleft
        end = pygame.Vector2(-4, 18) + self.frame.container_rect.topright
        for i in range(len(target_pokemon.moveset)):
            move = target_pokemon.moveset[i]
            pp_left = target_pokemon.moveset.pp[i]
            graphic = 35 if target_pokemon.moveset.selected[i] else 34
            color = text.LIME if pp_left else text.RED
            move_name_surface = (
                text.TextBuilder()
                .set_font(font_db.graphic_font)
                .write([graphic])
                .set_font(font_db.normal_font)
                .set_shadow(True)
                .set_color(color)
                .write(move.name)
                .build()
                .render()
            )
            self.menu_surface.blit(move_name_surface, start)
            start += pygame.Vector2(0, 16)

            pp_surface = text.TextBuilder.build_color(
                color, f"{pp_left}/{move.pp}"
            ).render()
            pp_rect = pp_surface.get_rect(topright=end)
            self.menu_surface.blit(pp_surface, pp_rect.topleft)
            end += pygame.Vector2(0, 16)

    def render_pointer(self, pointer: int, static_pointer=False):
        if static_pointer:
            surf = db.get_pointer()
        else:
            surf = self.pointer_animation.get_current_frame()
        pointer_position = (
            pygame.Vector2(self.frame.container_rect.topleft)
            + pygame.Vector2(0, 18)
            + pygame.Vector2(0, 16) * pointer
        )
        self.menu_surface.blit(surf, pointer_position)
