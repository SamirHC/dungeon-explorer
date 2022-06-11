import os
import xml.etree.ElementTree as ET
import pygame
import pygame.image
from dungeon_explorer.common import animation


class GroundMap:
    def __init__(self, bg: pygame.Surface, animations: list[animation.Animation], animation_positions: list[tuple[int, int]]):
        self.bg = bg
        self.animations = animations
        self.animation_positions = animation_positions

    def update(self):
        for anim in self.animations:
            anim.update()

    def render(self) -> pygame.Surface:
        surface = self.bg.copy()
        for anim, pos in zip(self.animations, self.animation_positions):
            surface.blit(anim.render(), pos)
        return surface


class GroundMapDatabase:
    def __init__(self):
        self.base_dir = os.path.join("assets", "images", "bg", "places")
        self.loaded: dict[str, GroundMap] = {}

    def __getitem__(self, ground_id: str) -> GroundMap:
        if ground_id not in self.loaded:
            self.load(ground_id)
        return self.loaded[ground_id]

    def load(self, ground_id: str):
        ground_dir = os.path.join(self.base_dir, ground_id)
        bg = pygame.image.load(os.path.join(ground_dir, f"{ground_id}_LOWER.png")).convert_alpha()

        root = ET.parse(os.path.join(ground_dir, "grounddata.xml")).getroot()
        
        objects = root.find("Objects").findall("Object")
        animations = []
        animation_positions = []
        for ob in objects:
            x = int(ob.get("x"))
            y = int(ob.get("y"))
            if ob.get("class") == "static":
                bg.blit(self.load_static_object(ob.get("id")), (x, y))
            elif ob.get("class") == "animated":
                animations.append(self.load_animated_object(ob.get("id")))
                animation_positions.append((x, y))
        
        self.loaded[ground_id] = GroundMap(bg, animations, animation_positions)

    def load_static_object(self, sprite_id: str):
        sprite_path = os.path.join("assets", "images", "bg_sprites", "static", f"{sprite_id}.png")
        return pygame.image.load(sprite_path).convert_alpha()

    def load_animated_object(self, sprite_id: str):
        sprite_dir = os.path.join("assets", "images", "bg_sprites", "animated", sprite_id)

        sprite_images_path = os.path.join(sprite_dir, f"{sprite_id}.png")
        sprite_images = pygame.image.load(sprite_images_path).convert_alpha()
        w, h = sprite_images.get_size()
        root = ET.parse(os.path.join(sprite_dir, "metadata.xml")).getroot()

        num_frames = int(root.get("frames"))
        w //= 4
        duration = int(root.get("duration"))
        frames = []
        for i in range(num_frames):
            frames.append(sprite_images.subsurface(i*w, 0, w, h))
        return animation.Animation(frames, [duration]*num_frames)

db = GroundMapDatabase()