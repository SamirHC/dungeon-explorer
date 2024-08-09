import os
import xml.etree.ElementTree as ET

import pygame

from app.common import constants
from app.model.animation import Animation


class BgSpriteDatabase:
    def __init__(self):
        self.base_dir = os.path.join(constants.IMAGES_DIRECTORY, "bg_sprites")
        self.static_dir = os.path.join(self.base_dir, "static")
        self.animated_dir = os.path.join(self.base_dir, "animated")
        self.loaded: dict[str, Animation] = {}

    def __getitem__(self, sprite_id: str) -> Animation:
        if sprite_id not in self.loaded:
            self.load(sprite_id)
        return self.loaded[sprite_id]

    def load(self, sprite_id: str):
        if os.path.exists(os.path.join(self.static_dir, f"{sprite_id}.png")):
            self.load_static_object(sprite_id)
        elif os.path.exists(os.path.join(self.animated_dir, sprite_id)):
            self.load_animated_object(sprite_id)

    def load_static_object(self, sprite_id: str):
        sprite_path = os.path.join(self.static_dir, f"{sprite_id}.png")
        # Save as Animation for uniformity, but it will just contain one frame
        self.loaded[sprite_id] = Animation(
            [pygame.image.load(sprite_path).convert_alpha()], [1]
        )

    def load_animated_object(self, sprite_id: str):
        sprite_dir = os.path.join(self.animated_dir, sprite_id)
        sprite_images_path = os.path.join(sprite_dir, f"{sprite_id}.png")
        sprite_metadata_path = os.path.join(sprite_dir, "metadata.xml")

        sprite_images = pygame.image.load(sprite_images_path).convert_alpha()
        root = ET.parse(sprite_metadata_path).getroot()
        
        num_frames = int(root.get("frames"))
        duration = int(root.get("duration"))
        w, h = sprite_images.get_size()
        w //= num_frames

        frames = []
        for i in range(num_frames):
            frames.append(sprite_images.subsurface(i * w, 0, w, h))

        self.loaded[sprite_id] = Animation(frames, [duration] * num_frames)
