import os

import pygame
import pygame.image
from dungeon_explorer.common import (animation, constants, inputstream, text,
                                     textbox)
from dungeon_explorer.pokemon import party, pokemon

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
        x_gap = 8 + pointer_surface.get_width()
        y_gap = 10
        spacing = 13
        surface = self.textbox_frame.copy()
        for i, option in enumerate(self.menu.options):
            x = x_gap
            y = y_gap + spacing * i
            surface.blit(text.build(option, constants.OFF_WHITE if self.active[i] else constants.RED), (x, y))
            if i == self.menu.pointer:
                surface.blit(pointer_animation.render(), (8, y))
        return surface


class MoveMenu:
    def __init__(self, party: party.Party):
        self.party = party
        self.frame = textbox.Frame((20, 14)).with_header_divider().with_footer_divider()
        self.menu = PagedMenuModel([[m.name for m in p.moveset if m.name != "Regular Attack"] for p in self.party])

    @property
    def target(self) -> pokemon.Pokemon:
        return self.party[self.menu.page]

    @property
    def page(self) -> int:
        return self.menu.page + 1

    def process_input(self, input_stream: inputstream.InputStream):
        kb = input_stream.keyboard
        if kb.is_pressed(pygame.K_s):
            self.menu.next()
        elif kb.is_pressed(pygame.K_w):
            self.menu.prev()
        elif kb.is_pressed(pygame.K_d):
            self.menu.next_page()
        elif kb.is_pressed(pygame.K_a):
            self.menu.prev_page()
        elif kb.is_pressed(pygame.K_RETURN):
            print(self.target.moveset[1+self.menu.pointer].name)

    def render(self):
        self.surface = pygame.Surface(self.frame.get_size(), pygame.SRCALPHA)
        self.surface.blit(self.frame, (0, 0))
        self.surface.blit(text.build_multicolor([(f"  {self.target.name}", self.target.name_color),("'s moves", constants.OFF_WHITE)]), self.frame.container_rect.topleft)

        end = pygame.Vector2(self.surface.get_width()-8, 8)
        page_num_surface = text.build(f"({self.page}/{len(self.party)})")
        page_num_rect = page_num_surface.get_rect(topright=end)
        self.surface.blit(page_num_surface, page_num_rect.topleft)
        
        start = pygame.Vector2(16, 16) + pygame.Vector2(8, 8)
        move_divider = text.text_divider(127)
        num_move_dividers = len(self.target.moveset) - 1
        for i in range(num_move_dividers):
            start += pygame.Vector2(0, 16)
            self.surface.blit(move_divider, start)
        
        start = pygame.Vector2(16, 18) + self.frame.container_rect.topleft
        end = pygame.Vector2(-4, 18) + self.frame.container_rect.topright
        for i in range(len(self.target.moveset)):
            if i == 0:
                continue
            move = self.target.moveset[i]
            pp_left = self.target.moveset.pp[i]
            color = constants.GREEN if pp_left else constants.RED
            
            self.surface.blit(text.build(move.name, color), start)
            start += pygame.Vector2(0, 16)

            pp_surface = text.build(f"{pp_left}/{move.pp}", color)
            pp_rect = pp_surface.get_rect(topright=end)
            self.surface.blit(pp_surface, pp_rect.topleft)
            end += pygame.Vector2(0, 16)

        return self.surface
