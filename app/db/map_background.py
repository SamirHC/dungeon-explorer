import os
import xml.etree.ElementTree as ET

import pygame

from app.common import constants
from app.ground.ground_map import MapBackground
from app.model.palette_animation import PaletteAnimation


class MapBackgroundDatabase:
    def __init__(self):
        self.base_dir = os.path.join(constants.IMAGES_DIRECTORY, "bg")
        self.loaded: dict[str, MapBackground] = {}

    def __getitem__(self, bg_id: str) -> MapBackground:
        if bg_id not in self.loaded:
            self.load(bg_id)
        return self.loaded[bg_id]

    def load(self, bg_id: str):
        folder_dict = {
            'D': "dungeon",
            'G': "guild",
            'H': "habitat",
            'P': "places",
            'S': "system",
            'T': "town",
            'V': "visual"
        }
        bg_dir = os.path.join(self.base_dir, folder_dict[bg_id[0]], bg_id)
        
        lower_bg_path = os.path.join(bg_dir, f"{bg_id}_LOWER.png")
        higher_bg_path = os.path.join(bg_dir, f"{bg_id}_HIGHER.png")
        palette_data_path = os.path.join(bg_dir, "palette_data.xml")
        metadata_path = os.path.join(bg_dir, "metadata.xml")

        lower_bg = pygame.image.load(lower_bg_path) if os.path.exists(lower_bg_path) else constants.EMPTY_SURFACE
        higher_bg = pygame.image.load(higher_bg_path) if os.path.exists(higher_bg_path) else constants.EMPTY_SURFACE

        palette_num, palette_animation = None, None
        if os.path.exists(palette_data_path):
            anim_root = ET.parse(palette_data_path).getroot()
            palette_num = self.get_palette_num(anim_root)
            palette_animation = self.get_palette_animation(anim_root)
        
        collisions = constants.EMPTY_SURFACE
        bg_sprites, bg_sprite_positions = [], []
        if os.path.exists(metadata_path):
            metadata_root = ET.parse(metadata_path).getroot()
            collisions = self.get_collision_mask_from_root(metadata_root)
            bg_sprites, bg_sprite_positions = self.get_bg_sprites(metadata_root)

        self.loaded[bg_id] = MapBackground(
            lower_bg,
            higher_bg,
            palette_num,
            palette_animation,
            collisions,
            bg_sprites,
            bg_sprite_positions
        )
        return self.loaded[bg_id]
    
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
        
        collision_node = root.find("Collision")
        rect_nodes = [] if collision_node is None else collision_node.findall("Rect")
        for rect_node in rect_nodes:
            x = int(rect_node.get("x"))
            y = int(rect_node.get("y"))
            width = int(rect_node.get("w"))
            height = int(rect_node.get("h"))
            
            rect = pygame.Rect(x, y, width, height)
            is_collision = bool(int(rect_node.get("value")))
            
            surface.fill((255, 0, 0, 128 if is_collision else 0), rect)
        
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
