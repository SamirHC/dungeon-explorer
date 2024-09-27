import os
import xml.etree.ElementTree as ET

import pygame

from app.common.constants import GAMEDATA_DIRECTORY, IMAGES_DIRECTORY
from app.item.item import Item, ItemCategory, ActionName


base_dir = os.path.join(GAMEDATA_DIRECTORY, "items")

ITEM_SIZE = 16
COLOR_KEY = pygame.Color(0, 127, 151)
COLOR_KEY_2 = pygame.Color(0, 127, 152)


def load(item_id: int) -> Item:
    item_path = os.path.join(base_dir, f"{item_id}.xml")
    root = ET.parse(item_path).getroot()
    sprite_id = int(root.get("sprite_id"))
    palette_id = int(root.get("palette_id"))
    category = ItemCategory[root.find("Category").text]
    buy_price = 0
    sell_price = 0
    name = root.find("Name").text
    short_desc = root.find("ShortDesc").text
    long_desc = root.find("LongDesc").text
    move_id = 0
    min_amount = 0
    max_amount = 0
    try:
        surface = load_image_2(item_id)
    except:
        surface = load_image(sprite_id, palette_id)
    return Item(
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
        ActionName.USE,
        surface,
    )


def load_image_2(item_id: int):
    surface = pygame.image.load(
        os.path.join(IMAGES_DIRECTORY, "item", f"{item_id}.png")
    ).convert_alpha()
    surface.set_colorkey(COLOR_KEY_2)
    return surface


def load_image(sprite_id: int, palette_id: int):
    item_sheet = pygame.image.load(
        os.path.join(IMAGES_DIRECTORY, "item", "items.png")
    ).convert_alpha()
    item_sheet.set_colorkey(COLOR_KEY)

    item_surf = pygame.Surface((ITEM_SIZE, ITEM_SIZE), pygame.SRCALPHA)
    x, y = sprite_id % 8, sprite_id // 8
    rect = pygame.Rect(
        x * ITEM_SIZE,
        y * ITEM_SIZE,
        ITEM_SIZE,
        ITEM_SIZE,
    )
    # TODO: change color palette based on palette_id
    item_surf.blit(item_sheet.subsurface(rect), (0, 0))
    return item_surf
