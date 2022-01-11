import constants
import pygame


class Animation:
    def __init__(self, frames: list[tuple[pygame.Surface, int]]):
        self.frames = frames
        self.restart()

    @property
    def total_duration(self) -> float:
        return self.total_frames / constants.FPS

    @property
    def total_frames(self) -> int:
        return sum(map(lambda x: x[1], self.frames))

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

    def play(self, animation_time_left, total_animation_time):
        for frame_count in range(len(self.frames)):
            if frame_count / len(self.frames) <= animation_time_left / total_animation_time < (frame_count + 1) / len(self.frames):
                self.index = frame_count
