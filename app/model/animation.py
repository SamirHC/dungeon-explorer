from typing import Sequence


class Animation:
    def __init__(self, frames: Sequence, durations: Sequence[int], iterations=-1):
        assert len(frames) == len(durations)
        self.frames = frames
        self.durations = durations
        self.iterations = iterations
        self.index = 0
        self.timer = 0

    def get_current_frame(self):
        if self.iterations == 0:
            return None
        return self.frames[self.index]

    def render(self):
        return self.get_current_frame()

    def restart(self):
        self.index = 0
        self.timer = 0

    def update(self):
        if self.iterations == 0:
            return
        self.timer = (self.timer + 1) % self.durations[self.index]
        if self.timer == 0:
            self.index = (self.index + 1) % len(self.frames)
        if self.is_restarted():
            self.iterations -= 1

    def is_restarted(self) -> bool:
        return self.index == 0 and self.timer == 0

    @classmethod
    def constant(cls, item):
        return cls([item], [1])
