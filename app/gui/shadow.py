from enum import Enum

from app.db import shadow


class ShadowSize(Enum):
    SMALL = 0
    MEDIUM = 1
    LARGE = 2


def get_black_shadow(size: ShadowSize):
    return [shadow.SMALL_BLACK, shadow.MEDIUM_BLACK, shadow.LARGE_BLACK][size.value]


def get_gold_shadow(size: ShadowSize):
    return [shadow.SMALL_GOLD, shadow.MEDIUM_GOLD, shadow.LARGE_GOLD][size.value]


def get_dungeon_shadow(size: ShadowSize, is_enemy: bool):
    return get_black_shadow(size) if is_enemy else get_gold_shadow(size)
