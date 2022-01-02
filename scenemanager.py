import pygame.display
import scene

class SceneManager:
    def __init__(self):
        self.scenes: list[scene.Scene] = []

    def add(self, s: scene.Scene):
        self.scenes.append(s)

    def pop(self) -> scene.Scene:
        if self.scenes:
            return self.scenes.pop()

    def current_scene(self) -> scene.Scene:
        if self.scenes:
            return self.scenes[-1]

    def process_input(self, keyboard_input):
        self.current_scene().process_input(keyboard_input)

    def update(self):
        self.current_scene().update()

    def render(self, display):
        self.current_scene().render()
        display.blit(self.current_scene().display, (0, 0))
        pygame.display.update()