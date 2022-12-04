import pygame


class Animation:
    def __init__(self, frames: list[pygame.Surface], durations: list[int]):
        self.frames = frames
        self.durations = durations
        self.restart()

    def render(self) -> pygame.Surface:
        return self.frames[self.index]

    def restart(self):
        self.index = 0
        self.timer = 0

    def update(self):
        self.timer += 1
        if self.timer == self.durations[self.index]:
            self.timer = 0
            self.index += 1
            if self.index == len(self.frames):
                self.index = 0

    def is_restarted(self) -> bool:
        return self.index == self.timer == 0


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
                self.indices[i] += 1
                if self.indices[i] == len(self.frames):
                    self.indices[i] = 0
                updated = True
        if updated:
            self.palette = self.current_palette()
        return updated

    def current_palette(self) -> list[pygame.Color]:
        return [self.frames[self.indices[i]][i] for i in range(self.palette_size)]
