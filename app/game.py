import pygame

from app.common import constants
from app.common import settings
from app.common.action import Action
from app.common.inputstream import InputStream
from app.db import database
import app.db.font as font_db
from app.gui import text


class Game:
    SCALED_SIZE = pygame.Vector2(constants.DISPLAY_SIZE) * 4
    CAPTION = "Pokémon Mystery Dungeon"

    def __init__(self, mode="continue"):
        pygame.init()
        self.display = pygame.display.set_mode(Game.SCALED_SIZE)
        font_db.init_fonts()

        pygame.display.set_caption(Game.CAPTION)
        pygame.display.set_icon(database.get_icon())

        self.clock = pygame.time.Clock()
        self.input_stream = InputStream()

        if mode == "intro":
            from app.scenes.intro_scene import IntroScene
            self.scene = IntroScene()
        elif mode == "continue":
            from app.scenes.main_menu_scene import MainMenuScene
            self.scene = MainMenuScene()
        elif mode == "story1":
            from app.scenes.story.chapter1 import story1
            self.scene = story1.Story1()

    def run(self):
        self.running = True
        while self.running:
            self.input()
            self.update()
            self.render()
        settings.save()
        pygame.quit()

    def input(self):
        self.input_stream.update()

        for ev in pygame.event.get():
            if (
                ev.type == pygame.QUIT
                or ev.type == pygame.KEYDOWN
                and ev.key == settings.get_key(Action.QUIT)
            ):
                self.handle_quit()

        self.scene.process_input(self.input_stream)

    def update(self):
        if self.scene.is_end:
            self.scene = self.scene.next_scene
        self.scene.update()

        self.clock.tick(constants.FPS)

    def handle_quit(self):
        self.running = False

    def render(self):
        surface = pygame.Surface(constants.DISPLAY_SIZE)
        surface.fill(constants.BLACK)
        scene_surf = self.scene.render()
        scene_surf.set_alpha(self.scene.alpha)
        surface.blit(scene_surf, (0, 0))
        surface.blit(self.render_fps(), (240, 8))
        self.display.blit(pygame.transform.scale(surface, Game.SCALED_SIZE), (0, 0))
        pygame.display.update()

    def render_fps(self) -> pygame.Surface:
        return text.TextBuilder.build_white(str(round(self.clock.get_fps()))).render()
