import constants
import pygame

class Animation:
    def __init__(self):
        self.frames = []
        self.index = 0
        self.is_loop = True

    @property
    def total_duration(self) -> float:
        return self.total_frames / constants.FPS

    @property
    def total_frames(self) -> int:
        return sum(self.durations)

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

    def play(self, animation_time_left, total_animation_time):
        for frame_count in range(len(self.frames)):
            if frame_count / len(self.frames) <= animation_time_left / total_animation_time < (frame_count + 1) / len(self.frames):
                self.index = frame_count