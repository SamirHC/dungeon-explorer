import os

import pygame
import pygame.display
import pygame.draw
import pygame.image
from dungeon_explorer.common import constants
from dungeon_explorer.dungeon import dungeon
from dungeon_explorer.pokemon import pokemon


class HudComponents:
    HUD_COMPONENTS_FILE = os.path.join(
        os.getcwd(), "assets", "images", "misc", "hud_components.png")
    SIZE = 8

    def __init__(self):
        self.hud_components = pygame.image.load(self.HUD_COMPONENTS_FILE)
        self.hud_components.set_colorkey(self.hud_components.get_at((0, 0)))

    def __getitem__(self, position: tuple[int, int]):
        x, y = position
        return self.hud_components.subsurface(x*self.SIZE, y*self.SIZE, self.SIZE, self.SIZE)

    def get_f(self) -> pygame.Surface:
        return self[10, 0]

    def get_l(self) -> pygame.Surface:
        return self[11, 0]

    def get_v(self) -> pygame.Surface:
        return self[12, 0]

    def get_b(self) -> pygame.Surface:
        return self[13, 1]

    def get_h(self) -> pygame.Surface:
        return self[10, 1]

    def get_p(self) -> pygame.Surface:
        return self[11, 1]

    def get_slash(self) -> pygame.Surface:
        return self[12, 1]

    def get_white_number(self, n: int) -> pygame.Surface:
        return self[n, 0]

    def get_green_number(self, n: int) -> pygame.Surface:
        return self[n, 1]


class Hud:    
    def __init__(self, target: pokemon.Pokemon, dungeon: dungeon.Dungeon):
        self.target = target
        self.dungeon = dungeon
        self.color = constants.ORANGE
        self.components = HudComponents()
        self.components.hud_components.set_palette_at(12, self.color)  # Makes the labelling text (e.g. B, F, Lv, HP) orange
        self.is_below = True

    def number_surface(self, n: int) -> pygame.Surface:
        s = str(n)
        surface = pygame.Surface((self.components.SIZE*len(s), self.components.SIZE), pygame.SRCALPHA)
        for i, digit in enumerate(s):
            surface.blit(self.components.get_white_number(int(digit)), (i*self.components.SIZE, 0))
        return surface

    def render(self) -> pygame.Surface:
        surface = pygame.Surface(constants.DISPLAY_SIZE, pygame.SRCALPHA)
        x = 0
        # Floor
        if self.is_below:
            surface.blit(self.components.get_b(), (x, 0))
            x += self.components.SIZE
        surface.blit(self.number_surface(self.dungeon.floor_number), (x, 0))
        x += len(str(self.dungeon.floor_number)) * self.components.SIZE
        surface.blit(self.components.get_f(), (x, 0))
        x += self.components.SIZE
        # Level
        surface.blit(self.components.get_l(), (x, 0))
        x += self.components.SIZE
        surface.blit(self.components.get_v(), (x, 0))
        x += self.components.SIZE
        surface.blit(self.number_surface(self.target.level), (x, 0))
        x += 4 * self.components.SIZE
        # HP
        surface.blit(self.components.get_h(), (x, 0))
        x += self.components.SIZE
        surface.blit(self.components.get_p(), (x, 0))
        x += self.components.SIZE
        j = x
        surface.blit(self.number_surface(self.target.hp), (x, 0))
        x += len(str(self.target.hp)) * self.components.SIZE
        surface.blit(self.components.get_slash(), (x, 0))
        x += self.components.SIZE
        surface.blit(self.number_surface(self.target.max_hp), (x, 0))
        x = j + 7 * self.components.SIZE  # 3 digit hp, slash, 3 digit max hp = max 7 components
        # HP bar
        pygame.draw.rect(surface, constants.RED, (x, 0, self.target.max_hp, self.components.SIZE))
        if self.target.hp > 0:
            pygame.draw.rect(surface, constants.GREEN, (x, 0, self.target.hp, self.components.SIZE))
        pygame.draw.rect(surface, constants.BLACK, (x, 0, self.target.max_hp, 2))
        pygame.draw.rect(surface, constants.BLACK, (x, 6, self.target.max_hp, 2))
        pygame.draw.rect(surface, constants.WHITE, (x, 0, self.target.max_hp, 1))
        pygame.draw.rect(surface, constants.WHITE, (x, 6, self.target.max_hp, 1))
        return surface
