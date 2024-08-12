import os

import pygame

from app.common import constants
import app.db.database as db
from app.gui import text
from app.scenes.scene import Scene


class Chapter1IntroScene(Scene):
    def __init__(self):
        super().__init__(60, 60)

        bg_path = os.path.join(
            constants.IMAGES_DIRECTORY,
            "bg",
            "visual",
            "V01P02A",
            "V01P02A_LOWER.png",
        )
        self.bg = pygame.image.load(bg_path).subsurface(
            pygame.Rect(0, 0, constants.DISPLAY_WIDTH, constants.DISPLAY_HEIGHT)
        )
        self.bg.set_alpha(128)

        self.chapter_number_banner = (
            text.TextBuilder()
            .set_font(db.font_db.banner_font)
            .set_alignment(text.Align.CENTER)
            .write("Chapter 1")
            .build()
            .render()
        )
        self.chapter_title_banner = (
            text.TextBuilder()
            .set_font(db.font_db.banner_font)
            .write("A Storm at Sea")
            .build()
            .render()
        )
        self.started_wait = False
        self.wait_start_time = 0
        self.WAIT_TIME = 1000

    def update(self):
        super().update()
        if self.in_transition:
            return
        if not self.started_wait:
            self.started_wait = True
            self.wait_start_time = pygame.time.get_ticks()
        if pygame.time.get_ticks() - self.wait_start_time < self.WAIT_TIME:
            return

        from app.scenes.story.chapter1.story0 import Story0

        self.next_scene = Story0()

    def render(self):
        surface = super().render()
        surface.blit(self.bg, (0, 0))
        cx = surface.get_rect().centerx
        rect = self.chapter_number_banner.get_rect(center=(cx, 72))
        surface.blit(self.chapter_number_banner, rect.topleft)
        rect = self.chapter_title_banner.get_rect(center=(cx, rect.bottom + 24))
        surface.blit(self.chapter_title_banner, rect.topleft)
        return surface
