import os

import pygame
import pygame.image
from dungeon_explorer.common import (animation, constants, inputstream, text,
                                     textbox)
from dungeon_explorer.pokemon import party, pokemon

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


class MenuOption:
    def __init__(self, size: tuple[int, int], name: str, active_color: pygame.Color=constants.OFF_WHITE):
        self.size = size
        self.name = name
        self.active_color = active_color
        self.is_active = True

    def deactivate(self):
        self.is_active = False

    def render(self):
        surface = pygame.Surface(self.size, pygame.SRCALPHA)
        surface.blit(text.build(self.name, self.active_color if self.is_active else constants.RED), (0, 0))
        return surface


class Menu:
    def __init__(self, size: tuple[int, int], options: list[str]):
        self.pointer_surface = pygame.image.load(os.path.join("assets", "images", "misc", "pointer.png"))
        self.pointer_surface.set_colorkey(self.pointer_surface.get_at((0, 0)))
        self.textbox_frame = textbox.Frame(size)
        self.options = [MenuOption((50, 13), op) for op in options]
        self._pointer = 0
        self.pointer_animation = animation.Animation([(self.pointer_surface, 30), (pygame.Surface((0, 0)), 30)])

    @property
    def current_option_name(self) -> str:
        return self.current_option.name

    @property
    def current_option(self) -> MenuOption:
        return self.options[self._pointer]

    def next(self):
        self.pointer_animation.restart()
        self._pointer = (self._pointer + 1) % len(self.options)

    def prev(self):
        self.pointer_animation.restart()
        self._pointer = (self._pointer - 1) % len(self.options)

    def process_input(self, input_stream: inputstream.InputStream):
        if input_stream.keyboard.is_pressed(pygame.K_s):
            self.next()
        elif input_stream.keyboard.is_pressed(pygame.K_w):
            self.prev()

    def update(self):
        self.pointer_animation.update()
    
    def render(self) -> pygame.Surface:
        x_gap = 8 + self.pointer_surface.get_width()
        y_gap = 10
        spacing = 13
        surface = self.textbox_frame.copy()
        for i, option in enumerate(self.options):
            x = x_gap
            y = y_gap + spacing * i
            surface.blit(option.render(), (x, y))
            if i == self._pointer:
                surface.blit(self.pointer_animation.render(), (8, y))
        return surface


class MoveMenu:
    def __init__(self, party: party.Party):
        self.party_index = 0
        self.party = party
        self.frame = textbox.Frame((20, 14)).with_header_divider().with_footer_divider()

    @property
    def target(self) -> pokemon.Pokemon:
        return self.party[self.party_index]

    @property
    def page(self) -> int:
        return self.party_index + 1

    def render(self):
        self.surface = pygame.Surface(self.frame.get_size(), pygame.SRCALPHA)
        self.surface.blit(self.frame, (0, 0))
        self.surface.blit(text.build_multicolor([(self.target.name, self.target.name_color),("'s moves", constants.OFF_WHITE)]), pygame.Vector2(8, 8)+pygame.Vector2(8, 0))

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
        
        start = pygame.Vector2(16, 18) + pygame.Vector2(8, 8)
        for i in range(len(self.target.moveset)):
            if i == 0:
                continue
            move = self.target.moveset[i]
            self.surface.blit(text.build(move.name, constants.GREEN), start)
            start += pygame.Vector2(0, 16)

        end = pygame.Vector2(self.surface.get_width()-8, 8) + pygame.Vector2(-4, 18)
        for i in range(len(self.target.moveset)):
            if i == 0:
                continue
            move = self.target.moveset[i]
            pp_left = self.target.moveset.pp[i]
            pp_surface = text.build(f"{pp_left}/{move.pp}", constants.GREEN)
            pp_rect = pp_surface.get_rect(topright=end)
            self.surface.blit(pp_surface, pp_rect.topleft)
            end += pygame.Vector2(0, 16)

        return self.surface
