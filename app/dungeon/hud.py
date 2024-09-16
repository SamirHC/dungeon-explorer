from typing import Callable

import pygame

from app.common import constants
from app.gui import text
import app.db.hud_components as hud_components_db
from app.dungeon.dungeon import Dungeon


HP_RED = pygame.Color(255, 125, 95)
HP_GREEN = pygame.Color(40, 248, 48)
ORANGE = pygame.Color(248, 128, 88)


class Hud:
    def __init__(self, dungeon: Dungeon):
        self.dungeon = dungeon

        self.target = dungeon.party.leader

        hud_components_db.set_palette_12(ORANGE)

    @property
    def get_number(self) -> Callable[[int], pygame.Surface]:
        return (
            hud_components_db.get_white_number
            if self.target is self.dungeon.party.leader
            else hud_components_db.get_green_number
        )

    def number_surface(self, n: int) -> pygame.Surface:
        s = str(n)
        surface = pygame.Surface(
            (hud_components_db.SIZE * len(s), hud_components_db.SIZE),
            pygame.SRCALPHA,
        )
        for i, digit in enumerate(s):
            surface.blit(self.get_number(int(digit)), (i * hud_components_db.SIZE, 0))
        return surface

    def update(self):
        pass

    def render(self) -> pygame.Surface:
        CURRENT_HP = self.target.status.hp.value
        TOTAL_HP = self.target.stats.hp.value
        LEVEL = self.target.stats.level.value
        FLOOR_NO = self.dungeon.floor_number

        surface = pygame.Surface(constants.DISPLAY_SIZE, pygame.SRCALPHA)

        x = 0
        # Floor
        if self.dungeon.dungeon_data.is_below:
            surface.blit(hud_components_db.get_b(), (x, 0))
            x += hud_components_db.SIZE
        surface.blit(self.number_surface(FLOOR_NO), (x, 0))
        x += len(str(FLOOR_NO)) * hud_components_db.SIZE
        surface.blit(hud_components_db.get_f(), (x, 0))
        x += hud_components_db.SIZE
        # Level
        surface.blit(hud_components_db.get_l(), (x, 0))
        x += hud_components_db.SIZE
        surface.blit(hud_components_db.get_v(), (x, 0))
        x += hud_components_db.SIZE
        surface.blit(self.number_surface(LEVEL), (x, 0))
        x += 4 * hud_components_db.SIZE
        # HP
        surface.blit(hud_components_db.get_h(), (72, 0))
        surface.blit(hud_components_db.get_p(), (80, 0))
        surface.blit(self.number_surface(CURRENT_HP), (88, 0))
        x = 88 + len(str(CURRENT_HP)) * hud_components_db.SIZE
        surface.blit(hud_components_db.get_slash(), (x, 0))
        x += hud_components_db.SIZE
        surface.blit(self.number_surface(TOTAL_HP), (x, 0))
        # 3 digit hp, slash, 3 digit max hp = max 7 components
        # HP bar
        pygame.draw.rect(
            surface,
            HP_RED,
            (144, 0, TOTAL_HP, hud_components_db.SIZE),
        )
        if CURRENT_HP > 0:
            pygame.draw.rect(
                surface,
                HP_GREEN,
                (144, 0, CURRENT_HP, hud_components_db.SIZE),
            )
        surface.blit(text.divider(TOTAL_HP), (144, 0))
        surface.blit(text.divider(TOTAL_HP), (144, 6))
        return surface
