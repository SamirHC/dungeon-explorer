import pygame
from app.common import constants
from app.dungeon.dungeon import Dungeon
from app.gui import text
from app.pokemon.pokemon import Pokemon
from app.gui.hudcomponents import HudComponents


HP_RED = pygame.Color(255, 125, 95)
HP_GREEN = pygame.Color(40, 248, 48)
ORANGE = pygame.Color(248, 128, 88)


class Hud:
    def __init__(self, target: Pokemon, dungeon: Dungeon):
        self.target = target
        self.dungeon = dungeon
        self.color = ORANGE
        self.components = HudComponents()
        self.components.set_palette_12(self.color)

    @property
    def get_number(self):
        return (
            self.components.get_white_number
            if self.target is self.dungeon.user
            else self.components.get_green_number
        )

    def number_surface(self, n: int) -> pygame.Surface:
        s = str(n)
        surface = pygame.Surface(
            (self.components.SIZE * len(s), self.components.SIZE), pygame.SRCALPHA
        )
        for i, digit in enumerate(s):
            surface.blit(self.get_number(int(digit)), (i * self.components.SIZE, 0))
        return surface

    def render(self) -> pygame.Surface:
        surface = pygame.Surface(constants.DISPLAY_SIZE, pygame.SRCALPHA)
        x = 0
        # Floor
        if self.dungeon.dungeon_data.is_below:
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
        surface.blit(self.number_surface(self.target.stats.level.value), (x, 0))
        x += 4 * self.components.SIZE
        # HP
        surface.blit(self.components.get_h(), (x, 0))
        x += self.components.SIZE
        surface.blit(self.components.get_p(), (x, 0))
        x += self.components.SIZE
        j = x
        surface.blit(self.number_surface(self.target.status.hp.value), (x, 0))
        x += len(str(self.target.status.hp.value)) * self.components.SIZE
        surface.blit(self.components.get_slash(), (x, 0))
        x += self.components.SIZE
        surface.blit(self.number_surface(self.target.stats.hp.value), (x, 0))
        x = (
            j + 7 * self.components.SIZE
        )  # 3 digit hp, slash, 3 digit max hp = max 7 components
        # HP bar
        pygame.draw.rect(surface, HP_RED, (x, 0, self.target.stats.hp.value, self.components.SIZE))
        if self.target.status.hp.value > 0:
            pygame.draw.rect(
                surface, HP_GREEN, (x, 0, self.target.status.hp.value, self.components.SIZE)
            )
        surface.blit(text.divider(self.target.stats.hp.value), (x, 0))
        surface.blit(text.divider(self.target.stats.hp.value), (x, 6))
        return surface
