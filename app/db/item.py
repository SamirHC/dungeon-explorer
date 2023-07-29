import os
import xml.etree.ElementTree as ET
from app.item import item
import pygame

class ItemDatabase:
    ITEM_SIZE = 16
    COLOR_KEY = pygame.Color(0, 127, 151)

    def __init__(self):
        self.base_dir = os.path.join("data", "gamedata", "items")
        self.item_sheet = pygame.image.load(os.path.join("assets", "images", "item", "items.png")).convert_alpha()
        self.item_sheet.set_colorkey(self.COLOR_KEY)
        self.loaded: dict[int, item.Item] = {}

    def __getitem__(self, item_id: int):
        if item_id not in self.loaded:
            self.load(item_id)
        return self.loaded[item_id]
    
    def load(self, item_id: int):
        item_path = os.path.join(self.base_dir, f"{item_id}.xml")
        root = ET.parse(item_path).getroot()
        sprite_id = int(root.get("sprite_id"))
        palette_id = int(root.get("palette_id"))
        category = item.ItemCategory[root.find("Category").text]
        buy_price = 0
        sell_price = 0
        name = root.find("Name").text
        short_desc = root.find("ShortDesc").text
        long_desc = root.find("LongDesc").text
        move_id = 0
        min_amount = 0
        max_amount = 0
        surface = self.load_image(sprite_id, palette_id)
        self.loaded[item_id] = item.Item(
            item_id,
            sprite_id,
            palette_id,
            category,
            buy_price,
            sell_price,
            name,
            short_desc,
            long_desc,
            move_id,
            min_amount,
            max_amount,
            item.ActionName.USE,
            surface
        )

    def load_image(self, sprite_id: int, palette_id: int):
        item_surf = pygame.Surface((self.ITEM_SIZE, self.ITEM_SIZE), pygame.SRCALPHA)
        x, y = sprite_id % 8, sprite_id // 8
        rect = pygame.Rect(x * self.ITEM_SIZE, y * self.ITEM_SIZE, self.ITEM_SIZE, self.ITEM_SIZE)
        # TODO: change color palette based on palette_id
        item_surf.blit(self.item_sheet.subsurface(rect), (0, 0))
        return item_surf