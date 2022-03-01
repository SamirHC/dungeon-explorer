from ..common import constants, inputstream
import pygame


class Scene:
    def __init__(self):
        self.next_scene = None
        self.is_destroyed = False

    def process_input(self, input_stream: inputstream.InputStream):
        pass

    def update(self):
        pass

    def render(self) -> pygame.Surface:
        return pygame.Surface(constants.DISPLAY_SIZE)


class TransitionScene(Scene):
    def __init__(self, t: int):
        super().__init__()
        self.timer = t

    def update(self):
        self.timer -= 1
        if self.timer == 0:
            self.is_destroyed = True
            return
