import os

import pygame

class HudComponents:
    HUD_COMPONENTS_FILE = os.path.join("assets", "images", "misc", "hud_components.png")
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

    # Sets the labelling text (e.g. B, F, Lv, HP)
    def set_palette_12(self, color: pygame.Color):
        self.hud_components.set_palette_at(12, color)
