import os
import pygame
import pygame.image

from app.common.constants import IMAGES_DIRECTORY
from app.model.animation import Animation


class StatAnimDatabase:
    def __init__(self):
        base_dir = os.path.join(IMAGES_DIRECTORY, "moves", "stat")
        fall_path = os.path.join(base_dir, "0.png")
        rise_path = os.path.join(base_dir, "1.png")
        reset_path = os.path.join(base_dir, "2.png")

        fall_sheet = pygame.image.load(fall_path)
        rise_sheet = pygame.image.load(rise_path)
        reset_sheet = pygame.image.load(reset_path)

        sheets = [fall_sheet, rise_sheet, reset_sheet]
        sizes = [(32, 48), (40, 48), (16, 16)]
        sheet_pairings = list(zip([0,1,2], sheets, sizes))

        accuracy_palette = (
            (0, 0, 0, 255),
            (241, 152, 249, 255),
            (243, 196, 237, 255),
            (255, 255, 255, 255),
        )
        attack_palette = (
            (0, 0, 0, 255),
            (236, 32, 32, 255),
            (250, 100, 100, 255),
            (255, 255, 255, 255),
        )
        defense_palette = (
            (0, 0, 0, 255),
            (42, 204, 42, 255),
            (121, 237, 56, 255),
            (255, 255, 255, 255),
        )
        sp_attack_palette = (
            (0, 0, 0, 255),
            (222, 127, 231, 255),
            (239, 164, 230, 255),
            (255, 255, 255, 255),
        )
        sp_defense_palette = (
            (0, 0, 0, 255),
            (153, 176, 183, 255),
            (182, 213, 226, 255),
            (255, 255, 255, 255),
        )
        evasion_palette = (
            (0, 0, 0, 255),
            (255, 210, 29, 255),
            (255, 241, 174, 255),
            (255, 255, 255, 255),
        )
        speed_palette = (
            (0, 0, 0, 255),
            (24, 156, 231, 255),
            (140, 222, 255, 255),
            (255, 255, 255, 255),
        )

        stat_names = [
            "accuracy",
            "attack",
            "defense",
            "sp_attack",
            "sp_defense",
            "evasion",
            "speed",
        ]
        palettes = [
            accuracy_palette,
            attack_palette,
            defense_palette,
            sp_attack_palette,
            sp_defense_palette,
            evasion_palette,
            speed_palette,
        ]
        pairings = list(zip(stat_names, palettes))

        self.anims = {
            (stat, anim_name): self.get_animation(sheet, palette, sizes)
            for stat, palette in pairings
            for anim_name, sheet, sizes in sheet_pairings
        }

    def get_sheet(
        self, sheet: pygame.Surface, palette: list[pygame.Color]
    ) -> pygame.Surface:
        new_sheet = sheet.copy()
        new_sheet.set_palette(palette)
        return new_sheet

    def get_animation(
        self, sheet: pygame.Surface, palette: list[pygame.Color], size: tuple[int, int]
    ) -> Animation:
        W, H = size
        NUM_FRAMES = sheet.get_width() // W

        new_sheet = self.get_sheet(sheet, palette)
        frames = list(
            map(lambda x: new_sheet.subsurface((x * W, 0, W, H)), range(NUM_FRAMES))
        )
        durations = [2] * NUM_FRAMES
        return Animation(frames, durations)

    def __getitem__(self, index: tuple[str, int]) -> Animation:
        return self.anims[index]
