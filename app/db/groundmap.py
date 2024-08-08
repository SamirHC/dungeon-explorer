import os
import xml.etree.ElementTree as ET

import pygame

from app.common import constants
from app.ground.ground_map import GroundMap
from app.model.palette_animation import PaletteAnimation


class GroundMapDatabase:
    def __init__(self):
        self.base_dir = os.path.join(constants.IMAGES_DIRECTORY, "bg", "places")
        self.loaded: dict[str, GroundMap] = {}

    def __getitem__(self, ground_id: str) -> GroundMap:
        if ground_id not in self.loaded:
            self.load(ground_id)
        return self.loaded[ground_id]

    def load(self, ground_id: str):
        ground_dir = os.path.join(self.base_dir, ground_id)
        root = ET.parse(os.path.join(ground_dir, "grounddata.xml")).getroot()
        
        lower_bg_path = os.path.join(ground_dir, f"{ground_id}_LOWER.png")
        lower_bg = pygame.image.load(lower_bg_path)
        
        higher_bg_path = os.path.join(ground_dir, f"{ground_id}_HIGHER.png")
        higher_bg = pygame.image.load(higher_bg_path) if os.path.exists(higher_bg_path) else constants.EMPTY_SURFACE

        palette_data_path = os.path.join(ground_dir, "palette_data.xml")
        palette_num, palette_animation = None, None
        if os.path.exists(palette_data_path):
            anim_root = ET.parse(palette_data_path).getroot()
            palette_num = self.get_palette_num(anim_root)
            palette_animation = self.get_palette_animation(anim_root)

        collisions = self.get_collision_mask_from_root(root)

        bg_sprites, bg_sprite_positions = self.get_bg_sprites(root)

        self.loaded[ground_id] = GroundMap(
            lower_bg,
            higher_bg,
            palette_num,
            palette_animation,
            collisions,
            bg_sprites,
            bg_sprite_positions
        )
        return self.loaded[ground_id]
    
    def get_palette_num(self, root: ET.Element) -> int:
        return int(root.get("palette"))
        
    def get_palette_animation(self, root: ET.Element) -> PaletteAnimation:
        frames = root.findall("Frame")
        return PaletteAnimation(
            [
                [pygame.Color(f"#{color.text}") for color in frame.findall("Color")]
                for frame in frames
            ],
            [int(frames[0].get("duration"))] * len(frames[0]),
        )

    def get_collision_mask_from_root(self, root: ET.Element) -> pygame.Surface:
        w, h = int(root.get("width")), int(root.get("height"))
        surface = pygame.Surface((w // 8, h // 8), pygame.SRCALPHA)
        
        rects = root.find("Collision").findall("Rect")
        for rect in rects:
            x = int(rect.get("x"))
            y = int(rect.get("y"))
            width = int(rect.get("w"))
            height = int(rect.get("h"))
            
            py_rect = pygame.Rect(x, y, width, height)
            is_collision = bool(int(rect.get("value")))
            
            surface.fill((255, 0, 0, 128 if is_collision else 0), py_rect)
        
        return pygame.transform.scale(surface, (w, h))
    
    def get_bg_sprites(self, root: ET.Element):
        from app.db.database import bg_sprite_db

        bg_sprites = []
        bg_sprite_positions = []
        
        objects = root.find("Objects").findall("Object")
        for ob in objects:
            x = int(ob.get("x"))
            y = int(ob.get("y"))

            bg_sprites.append(bg_sprite_db[ob.get("id")])
            bg_sprite_positions.append((x, y))
        
        return bg_sprites, bg_sprite_positions
