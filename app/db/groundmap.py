import os
import xml.etree.ElementTree as ET
import pygame

from app.ground.groundmap import GroundMap
from app.common import animation


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
        lower_bg = pygame.image.load(os.path.join(ground_dir, f"{ground_id}_LOWER.png"))

        try:
            higher_bg = pygame.image.load(os.path.join(ground_dir, f"{ground_id}_HIGHER.png"))
        except:
            higher_bg = pygame.Surface((0, 0), pygame.SRCALPHA)

        try:
            anim_root = ET.parse(os.path.join(ground_dir, f"palette_data.xml")).getroot()
            palette_num = int(anim_root.get("palette"))
            frames = anim_root.findall("Frame")
            palette_animation = animation.PaletteAnimation(
                [[pygame.Color(f"#{color.text}") for color in frame.findall("Color")] for frame in frames],
                [int(frames[0].get("duration"))]*len(frames[0])
            )
        except:
            palette_num = None
            palette_animation = None

        root = ET.parse(os.path.join(ground_dir, "grounddata.xml")).getroot()

        collisions = {(x, y): False for x in range(lower_bg.get_width() // 8) for y in range(lower_bg.get_height() // 8)}
        rects = root.find("Collision").findall("Rect")
        for rect in rects:
            x = int(rect.get("x"))
            y = int(rect.get("y"))
            width = int(rect.get("width"))
            height = int(rect.get("height"))
            for i in range(width):
                for j in range(height):
                    val = rect.get("value")
                    if val is not None:
                        collisions[x+i, y+j] = bool(int(val))
        
        objects = root.find("Objects").findall("Object")
        animations = []
        animation_positions = []
        static = []
        static_positions = []
        for ob in objects:
            x = int(ob.get("x"))
            y = int(ob.get("y"))
            if ob.get("class") == "static":
                static.append(self.load_static_object(ob.get("id")))
                static_positions.append((x, y))
            elif ob.get("class") == "animated":
                animations.append(self.load_animated_object(ob.get("id")))
                animation_positions.append((x, y))
        
        self.loaded[ground_id] = GroundMap(
            lower_bg,
            higher_bg,
            palette_num,
            palette_animation,
            collisions,
            animations,
            animation_positions,
            static,
            static_positions
        )

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
