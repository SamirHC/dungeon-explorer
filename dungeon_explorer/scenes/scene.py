import pygame
from dungeon_explorer.common import constants, inputstream


class Scene:
    def __init__(self, fade_in: int=0, fade_out: int=0):
        self.fade_in = fade_in
        self.fade_out = fade_out
        self.t = fade_in
        self.alpha = 0
        self._next_scene = None

    @property
    def in_transition(self) -> bool:
        return self.t or self.next_scene is not None

    @property
    def is_end(self) -> bool:
        return self.next_scene and not self.t

    @property
    def next_scene(self):
        return self._next_scene
    @next_scene.setter
    def next_scene(self, scene):
        self._next_scene = scene
        self.t = self.fade_out

    def process_input(self, input_stream: inputstream.InputStream):
        pass

    def update(self):
        if self.in_transition:
            self.t -= 1
            if self.fade_out and self.next_scene:
                self.alpha = 255 * self.t / self.fade_out
            elif self.fade_in:
                self.alpha = 255 * (1 - self.t / self.fade_in)
            return

    def render(self) -> pygame.Surface:
        return pygame.Surface(constants.DISPLAY_SIZE)


class TransitionScene(Scene):
    def __init__(self, t: int):
        super().__init__()
        self.timer = 0
        self.end_time = t

    def update(self):
        self.timer += 1
        if self.timer == self.end_time:
            self.end_scene()

    def end_scene(self):
        pass
