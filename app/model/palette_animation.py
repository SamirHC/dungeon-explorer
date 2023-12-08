import pygame
from app.model.animation import Animation


PALETTE_SIZE = 16


class PaletteAnimation:
    """
    A palette is a list containing 16 colours.
    Palettes: List of palettes.
    Durations: This does NOT represent how long a palette is held for. Instead,
               it measures how long each color in the palette is held for.
    """

    def __init__(self, palettes: list[list[pygame.Color]], durations: list[int]):
        assert len(durations) == PALETTE_SIZE
        for palette in palettes:
            assert len(palette) == PALETTE_SIZE

        self.color_frames = [
            [palette[i] for palette in palettes] for i in range(PALETTE_SIZE)
        ]
        self.durations = [[t] * len(palettes) for t in durations]

        self.animations = [
            Animation(frames, durations)
            for frames, durations in zip(self.color_frames, self.durations)
        ]

    def update(self):
        for anim in self.animations:
            anim.update()

    def current_palette(self) -> list[pygame.Color]:
        return [anim.get_current_frame() for anim in self.animations]

    def set_palette(self, surf: pygame.Surface, animation_index: int):
        palette = self.current_palette()
        for i in range(PALETTE_SIZE):
            surf.set_palette_at(animation_index * PALETTE_SIZE + i, palette[i])
