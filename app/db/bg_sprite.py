import functools
import os
import xml.etree.ElementTree as ET

import pygame

from app.common import constants
from app.model.animation import Animation


base_dir = os.path.join(constants.IMAGES_DIRECTORY, "bg_sprites")
static_dir = os.path.join(base_dir, "static")
animated_dir = os.path.join(base_dir, "animated")


@functools.cache
def load(sprite_id: str) -> Animation:
    if os.path.exists(os.path.join(static_dir, f"{sprite_id}.png")):
        return _load_static_object(sprite_id)
    elif os.path.exists(os.path.join(animated_dir, sprite_id)):
        return _load_animated_object(sprite_id)


# Save as Animation for uniformity, but it will just contain one frame
def _load_static_object(sprite_id: str) -> Animation:
    sprite_path = os.path.join(static_dir, f"{sprite_id}.png")
    return Animation([pygame.image.load(sprite_path).convert_alpha()], [1])


def _load_animated_object(sprite_id: str) -> Animation:
    sprite_dir = os.path.join(animated_dir, sprite_id)
    sprite_images_path = os.path.join(sprite_dir, f"{sprite_id}.png")
    sprite_metadata_path = os.path.join(sprite_dir, "metadata.xml")

    sprite_images = pygame.image.load(sprite_images_path).convert_alpha()
    root = ET.parse(sprite_metadata_path).getroot()

    num_frames = int(root.get("frames"))
    duration = int(root.get("duration"))
    w, h = sprite_images.get_size()
    w //= num_frames

    frames = [sprite_images.subsurface(i * w, 0, w, h) for i in range(num_frames)]

    return Animation(frames, [duration] * num_frames)
