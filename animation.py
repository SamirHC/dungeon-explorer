class Animation:
    def __init__(self):
        self.frames = []
        self.index = 0
        self.is_loop = True

    def set_frames(self, frames):
        self.frames = frames

    def get_current_frame(self):
        return self.frames[self.index]

    def next(self):
        self.index += 1
        if self.index == len(self.frames) and not self.is_loop:
            return
        self.index %= len(self.frames)
        return self.get_current_frame()