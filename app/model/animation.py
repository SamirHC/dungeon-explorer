import pygame


class Animation:
    def __init__(self, frames: list, durations: list[int], iterations=-1):
        self.frames = frames
        self.durations = durations
        self.iterations = iterations
        self.index = 0
        self.timer = 0

    def get_current_frame(self):
        if self.iterations == 0:
            return None
        return self.frames[self.index]

    def restart(self):
        self.index = 0
        self.timer = 0

    def update(self):
        if self.iterations == 0:
            return
        self.timer = (self.timer + 1) % self.durations[self.index]
        if self.timer == 0:
            self.index = (self.index + 1) % len(self.frames)
        if self.index == 0:
            self.iterations -= 1

    def is_restarted(self) -> bool:
        return self.index == 0 and self.timer == 0


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
