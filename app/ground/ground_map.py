import dataclasses

import pygame
import pygame.image

from app.model.animation import Animation
from app.model.palette_animation import PaletteAnimation



"""
Represents the background map of the game in "Ground mode". This is where story
scenes and other non-dungeon gameplay takes place.
"""


@dataclasses.dataclass
class GroundMap:
    lower_bg: pygame.Surface
    higher_bg: pygame.Surface
    palette_num: int
    palette_animation: PaletteAnimation
    collision: pygame.Surface
    animations: list[Animation]
    animation_positions: list[tuple[int, int]]
    static: list[pygame.Surface]
    static_positions: list[tuple[int, int]]

    render_toggle = True

    def update(self):
        for anim in self.animations:
            anim.update()
        if self.palette_num is not None:
            self.palette_animation.update()
            self.palette_animation.set_palette(self.lower_bg, self.palette_num)

    def render(self) -> pygame.Surface:
        surface = pygame.Surface(self.lower_bg.get_size(), pygame.SRCALPHA)
        surface.blit(self.lower_bg, (0, 0))
        surface.blit(self.higher_bg, (0, 0))
        for anim, pos in zip(self.animations, self.animation_positions):
            surface.blit(anim.get_current_frame(), pos)
        for static, pos in zip(self.static, self.static_positions):
            surface.blit(static, pos)

        if self.render_toggle:
            surface.blit(self.collision, (0, 0))

        return surface
