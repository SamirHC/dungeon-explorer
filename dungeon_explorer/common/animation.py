import pygame


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
