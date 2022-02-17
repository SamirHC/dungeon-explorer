import pygame
import xml.etree.ElementTree as ET


class Animation:
    def __init__(self, frames: list[tuple[pygame.Surface, int]]):
        self.frames = frames
        self.restart()

    def get_duration(self, index) -> int:
        return self.frames[index][1]

    def render(self) -> pygame.Surface:
        return self.frames[self.index][0]

    def restart(self):
        self.index = 0
        self.timer = 0
        self.iterations = 0

    def update(self):
        self.timer += 1
        if self.timer == self.get_duration(self.index):
            self.timer = 0
            self.index += 1
            if self.index == len(self.frames):
                self.index = 0
                self.iterations += 1


class PaletteAnimation:
    def __init__(self, root: ET.Element):
        self.frames = root.findall("Frame")
        self.durations = [int(el.get("duration")) for el in self.frames[0].findall("Color")]
        self.palette_size = len(self.durations)
        self.colors = [[pygame.Color(f"#{color.text}") for color in frame] for frame in self.frames]
        self.timer = 0
        self.indices = [0] * self.palette_size
        self.palette = self.current_palette()
    
    def update(self):
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

    def current_palette(self):
        return [self.colors[self.indices[i]] for i in range(self.palette_size)]