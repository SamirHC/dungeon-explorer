import pygame
from dungeon_explorer.common import constants, inputstream


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
        self.timer = 0
        self.end_time = t

    def update(self):
        self.timer += 1
        if self.timer == self.end_time:
            self.end_scene()

    def end_scene(self):
        pass
