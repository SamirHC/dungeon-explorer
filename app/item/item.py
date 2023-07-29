from dataclasses import dataclass
from enum import Enum, auto
import pygame

class ItemCategory(Enum):
    THROWN_PIERCE = auto()
    THROWN_ROCK = auto()
    BERRIES_SEEDS_VITAMINS = auto()
    FOODS_GUMMIES = auto()
    HOLD = auto()
    TMS_HMS = auto()
    MONEY = auto()
    ORBS = auto()
    LINK_BOX = auto()
    USED_TM = auto()
    TREASURE_BOX = auto()
    EXCLUSIVE_ITEMS = auto()
    OTHER = auto()

class ActionName(Enum):
    USE = auto()
    HURL = auto()
    THROW = auto()
    HOLD = auto()
    EAT = auto()
    INGEST = auto()

@dataclass
class Item:
    item_id: int
    sprite_id: int
    palette_id: int
    category: ItemCategory
    buy_price: int
    sell_price: int
    name: str
    short_description: str
    long_description: str
    move_id: int
    min_amount: int
    max_amount: int
    action_name: str
    surface: pygame.Surface
