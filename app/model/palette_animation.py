import pygame


class PaletteAnimation:
    def __init__(self, palettes: list[list[pygame.Color]], durations: list[int]):
        self.frames = palettes
        self.durations = durations
        self.palette_size = len(durations)
        self.timer = 0
        self.indices = [0] * self.palette_size
        self.palette = self.current_palette()

    def update(self) -> bool:
        updated = False
        self.timer += 1
        for i, t in enumerate(self.durations):
            if self.timer % t == 0:
                self.indices[i] = (self.indices[i] + 1) % len(self.frames)
                updated = True
        if updated:
            self.palette = self.current_palette()
        return updated

    def current_palette(self) -> list[pygame.Color]:
        return [self.frames[self.indices[i]][i] for i in range(self.palette_size)]
