import pygame

class Animation:
    def __init__(self):
        self.frames = []
        self.index = 0
        self.is_loop = True

    def set_frames(self, frames: list[pygame.Surface]):
        self.frames = frames

    def set_durations(self, durations: list[int]):
        self.durations = durations

    def get_current_frame(self) -> pygame.Surface:
        return self.frames[self.index]

    def next(self):
        self.index += 1
        if self.index == len(self.frames) and not self.is_loop:
            return
        self.index %= len(self.frames)
        return self.get_current_frame()