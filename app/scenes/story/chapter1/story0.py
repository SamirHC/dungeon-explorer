import pygame

from app.common.inputstream import InputStream
from app.scenes.scene import Scene


class Story0(Scene):
    def __init__(self):
        super().__init__(30, 30)
    
    def process_input(self, input_stream: InputStream):
        return super().process_input(input_stream)
    
    def update(self):
        return super().update()
    
    def render(self) -> pygame.Surface:
        return super().render()
