import pygame
import pygame.display
import inputstream
import scene


class SceneManager:
    def __init__(self):
        self.scenes = [scene.DungeonScene("BeachCave", "0025")]
        #self.scenes: list[scene.Scene] = [scene.MainMenuScene()]

    def add(self, s: scene.Scene):
        self.scenes.append(s)

    def pop(self) -> scene.Scene:
        return self.scenes.pop()

    @property
    def current_scene(self) -> scene.Scene:
        return self.scenes[-1]

    def process_input(self, input_stream: inputstream.InputStream):
        self.current_scene.process_input(input_stream)

    def update(self):
        self.current_scene.update()

    def render(self, display: pygame.Surface):
        display.blit(self.current_scene.render(), (0, 0))
        pygame.display.update()
