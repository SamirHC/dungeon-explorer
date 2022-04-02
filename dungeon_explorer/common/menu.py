import os

import pygame
import pygame.image
from dungeon_explorer.common import (animation, constants, inputstream, text,
                                     textbox)
from dungeon_explorer.pokemon import party, pokemon, move, pokemondata

pointer_surface = pygame.image.load(os.path.join("assets", "images", "misc", "pointer.png"))
pointer_surface.set_colorkey(pointer_surface.get_at((0, 0)))
pointer_animation = animation.Animation([(pointer_surface, 30), (pygame.Surface((0, 0)), 30)])

class MenuModel:
    def __init__(self, options: list[str]):
        self.options = options
        self.pointer = 0

    def next(self):
        self.pointer = (self.pointer + 1) % len(self.options)

    def prev(self):
        self.pointer = (self.pointer - 1) % len(self.options)

    @property
    def current_option(self) -> str:
        return self.options[self.pointer]


class PagedMenuModel(MenuModel):
    def __init__(self, pages: list[list[str]]):
        self.page = 0
        self.pages = pages
        super().__init__(self.pages[self.page])

    def next_page(self):
        self.page = (self.page + 1) % len(self.pages)
        self.options = self.pages[self.page]
        self.pointer = 0

    def prev_page(self):
        self.page = (self.page - 1) % len(self.pages)
        self.options = self.pages[self.page]
        self.pointer = 0


class Menu:
    def __init__(self, size: tuple[int, int], options: list[str]):
        self.textbox_frame = textbox.Frame(size)
        self.menu = MenuModel(options)
        self.active = [True for _ in options]

    @property
    def pointer(self) -> int:
        return self.menu.pointer
    @pointer.setter
    def pointer(self, value: int):
        self.menu.pointer = value

    @property
    def current_option(self) -> str:
        return self.menu.current_option

    def next(self):
        pointer_animation.restart()
        self.menu.next()

    def prev(self):
        pointer_animation.restart()
        self.menu.prev()

    def process_input(self, input_stream: inputstream.InputStream):
        if input_stream.keyboard.is_pressed(pygame.K_s):
            self.next()
        elif input_stream.keyboard.is_pressed(pygame.K_w):
            self.prev()

    def update(self):
        pointer_animation.update()
    
    def render(self) -> pygame.Surface:
        surface = self.textbox_frame.copy()
        x, y = self.textbox_frame.container_rect.topleft
        y += 2
        dx = pointer_surface.get_width() + 1
        dy = pointer_surface.get_height() + 2
        for i, option in enumerate(self.menu.options):
            if i == self.menu.pointer:
                surface.blit(pointer_animation.render(), (x, y))
            text_surface = text.build(option, constants.OFF_WHITE if self.active[i] else constants.RED)
            surface.blit(text_surface, (x + dx, y))
            y += dy
        
        return surface


class MoveMenu:
    def __init__(self, party: party.Party):
        self.party = party
        self.frame = textbox.Frame((20, 14)).with_header_divider().with_footer_divider()
        self.menu = PagedMenuModel([[m.name for m in p.moveset] for p in self.party])
        self.frozen = False

    @property
    def page(self) -> int:
        return self.menu.page

    @property
    def pointer(self) -> int:
        return self.menu.pointer

    @property
    def target_pokemon(self) -> pokemon.Pokemon:
        return self.party[self.menu.page]

    @property
    def target_moveset(self) -> pokemondata.Moveset:
        return self.target_pokemon.moveset

    @property
    def target_move(self) -> move.Move:
        return self.target_moveset[self.pointer]

    @property
    def display_page(self) -> int:
        return self.menu.page + 1

    def shift_up(self):
        self.menu.pointer = self.target_moveset.shift_up(self.pointer)

    def shift_down(self):
        self.menu.pointer = self.target_moveset.shift_down(self.pointer)

    def process_input(self, input_stream: inputstream.InputStream):
        kb = input_stream.keyboard
        if kb.is_pressed(pygame.K_s):
            pointer_animation.restart()
            self.menu.next()
        elif kb.is_pressed(pygame.K_w):
            pointer_animation.restart()
            self.menu.prev()
        elif kb.is_pressed(pygame.K_d):
            pointer_animation.restart()
            self.menu.next_page()
        elif kb.is_pressed(pygame.K_a):
            pointer_animation.restart()
            self.menu.prev_page()
        elif kb.is_pressed(pygame.K_RETURN):
            print(self.target_move.name)

    def update(self):
        pointer_animation.update()

    def render(self):
        self.surface = pygame.Surface(self.frame.get_size(), pygame.SRCALPHA)
        self.render_frame()
        self.render_title()
        self.render_page_num()
        self.render_move_dividers()
        self.render_move_name_pp()
        self.render_pointer()
        return self.surface

    def render_frame(self):
        self.surface.blit(self.frame, (0, 0))

    def render_title(self):
        title = text.build_multicolor([(f"  {self.target_pokemon.name}", self.target_pokemon.name_color),("'s moves", constants.OFF_WHITE)])
        self.surface.blit(title, self.frame.container_rect.topleft)

    def render_page_num(self):
        end = pygame.Vector2(self.surface.get_width()-8, 8)
        page_num_surface = text.build(f"({self.display_page}/{len(self.party)})")
        page_num_rect = page_num_surface.get_rect(topright=end)
        self.surface.blit(page_num_surface, page_num_rect.topleft)

    def render_move_dividers(self):
        start = pygame.Vector2(16, 16) + pygame.Vector2(8, 8)
        move_divider = text.text_divider(127)
        num_move_dividers = len(self.target_moveset) - 1
        for i in range(num_move_dividers):
            start += pygame.Vector2(0, 16)
            self.surface.blit(move_divider, start)

    def render_move_name_pp(self):
        start = pygame.Vector2(16, 18) + self.frame.container_rect.topleft
        end = pygame.Vector2(-4, 18) + self.frame.container_rect.topright
        for i in range(len(self.target_moveset)):
            move = self.target_moveset[i]
            pp_left = self.target_moveset.pp[i]
            color = constants.GREEN if pp_left else constants.RED
            
            self.surface.blit(text.build(move.name, color), start)
            start += pygame.Vector2(0, 16)

            pp_surface = text.build(f"{pp_left}/{move.pp}", color)
            pp_rect = pp_surface.get_rect(topright=end)
            self.surface.blit(pp_surface, pp_rect.topleft)
            end += pygame.Vector2(0, 16)

    def render_pointer(self):
        if self.frozen:
            surf = pointer_surface
        else:
            surf = pointer_animation.render()
        pointer_position = pygame.Vector2(self.frame.container_rect.topleft) + pygame.Vector2(0, 18) + pygame.Vector2(0, 16)*self.menu.pointer
        self.surface.blit(surf, pointer_position)
