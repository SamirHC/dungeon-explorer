from __future__ import annotations

import dataclasses

import pygame

from app.dungeon.tile_type import TileType
from app.model.palette_animation import PaletteAnimation
from app.dungeon.terrain import Terrain


tile_masks = {
    11: (0, 0),
    139: (0, 0),
    43: (0, 0),
    171: (0, 0),
    15: (0, 0),
    143: (0, 0),
    47: (0, 0),
    175: (0, 0),
    31: (1, 0),
    159: (1, 0),
    63: (1, 0),
    191: (1, 0),
    22: (2, 0),
    150: (2, 0),
    54: (2, 0),
    182: (2, 0),
    23: (2, 0),
    151: (2, 0),
    55: (2, 0),
    183: (2, 0),
    10: (3, 0),
    138: (3, 0),
    42: (3, 0),
    170: (3, 0),
    14: (3, 0),
    142: (3, 0),
    46: (3, 0),
    174: (3, 0),
    24: (4, 0),
    152: (4, 0),
    56: (4, 0),
    184: (4, 0),
    28: (4, 0),
    156: (4, 0),
    60: (4, 0),
    188: (4, 0),
    25: (4, 0),
    153: (4, 0),
    57: (4, 0),
    185: (4, 0),
    29: (4, 0),
    157: (4, 0),
    61: (4, 0),
    189: (4, 0),
    18: (5, 0),
    146: (5, 0),
    50: (5, 0),
    178: (5, 0),
    19: (5, 0),
    147: (5, 0),
    51: (5, 0),
    179: (5, 0),
    107: (0, 1),
    235: (0, 1),
    111: (0, 1),
    239: (0, 1),
    255: (1, 1),
    214: (2, 1),
    246: (2, 1),
    215: (2, 1),
    247: (2, 1),
    66: (3, 1),
    194: (3, 1),
    98: (3, 1),
    226: (3, 1),
    70: (3, 1),
    198: (3, 1),
    102: (3, 1),
    230: (3, 1),
    67: (3, 1),
    195: (3, 1),
    99: (3, 1),
    227: (3, 1),
    71: (3, 1),
    199: (3, 1),
    103: (3, 1),
    231: (3, 1),
    0: (4, 1),
    128: (4, 1),
    32: (4, 1),
    160: (4, 1),
    4: (4, 1),
    132: (4, 1),
    36: (4, 1),
    164: (4, 1),
    1: (4, 1),
    129: (4, 1),
    33: (4, 1),
    161: (4, 1),
    5: (4, 1),
    133: (4, 1),
    37: (4, 1),
    165: (4, 1),
    80: (5, 1),
    112: (5, 1),
    84: (5, 1),
    116: (5, 1),
    81: (5, 1),
    113: (5, 1),
    85: (5, 1),
    117: (5, 1),
    104: (0, 2),
    232: (0, 2),
    108: (0, 2),
    236: (0, 2),
    105: (0, 2),
    233: (0, 2),
    109: (0, 2),
    237: (0, 2),
    248: (1, 2),
    252: (1, 2),
    249: (1, 2),
    253: (1, 2),
    208: (2, 2),
    240: (2, 2),
    212: (2, 2),
    244: (2, 2),
    209: (2, 2),
    241: (2, 2),
    213: (2, 2),
    245: (2, 2),
    72: (3, 2),
    200: (3, 2),
    76: (3, 2),
    204: (3, 2),
    73: (3, 2),
    201: (3, 2),
    77: (3, 2),
    205: (3, 2),
    2: (4, 2),
    130: (4, 2),
    34: (4, 2),
    162: (4, 2),
    6: (4, 2),
    134: (4, 2),
    38: (4, 2),
    166: (4, 2),
    3: (4, 2),
    131: (4, 2),
    35: (4, 2),
    163: (4, 2),
    7: (4, 2),
    135: (4, 2),
    39: (4, 2),
    167: (4, 2),
    222: (0, 3),
    123: (1, 3),
    26: (2, 3),
    154: (2, 3),
    58: (2, 3),
    186: (2, 3),
    8: (3, 3),
    136: (3, 3),
    40: (3, 3),
    168: (3, 3),
    12: (3, 3),
    140: (3, 3),
    44: (3, 3),
    172: (3, 3),
    9: (3, 3),
    137: (3, 3),
    41: (3, 3),
    169: (3, 3),
    13: (3, 3),
    141: (3, 3),
    45: (3, 3),
    173: (3, 3),
    90: (4, 3),
    16: (5, 3),
    144: (5, 3),
    48: (5, 3),
    176: (5, 3),
    20: (5, 3),
    148: (5, 3),
    52: (5, 3),
    180: (5, 3),
    17: (5, 3),
    145: (5, 3),
    49: (5, 3),
    177: (5, 3),
    21: (5, 3),
    149: (5, 3),
    53: (5, 3),
    181: (5, 3),
    95: (0, 4),
    250: (1, 4),
    88: (2, 4),
    92: (2, 4),
    89: (2, 4),
    93: (2, 4),
    74: (3, 4),
    202: (3, 4),
    78: (3, 4),
    206: (3, 4),
    64: (4, 4),
    192: (4, 4),
    96: (4, 4),
    224: (4, 4),
    68: (4, 4),
    196: (4, 4),
    100: (4, 4),
    228: (4, 4),
    65: (4, 4),
    193: (4, 4),
    97: (4, 4),
    225: (4, 4),
    69: (4, 4),
    197: (4, 4),
    101: (4, 4),
    229: (4, 4),
    82: (5, 4),
    114: (5, 4),
    83: (5, 4),
    115: (5, 4),
    254: (0, 5),
    251: (1, 5),
    106: (2, 5),
    234: (2, 5),
    110: (2, 5),
    238: (2, 5),
    210: (3, 5),
    242: (3, 5),
    211: (3, 5),
    243: (3, 5),
    30: (4, 5),
    158: (4, 5),
    62: (4, 5),
    190: (4, 5),
    27: (5, 5),
    155: (5, 5),
    59: (5, 5),
    187: (5, 5),
    223: (0, 6),
    127: (1, 6),
    75: (2, 6),
    203: (2, 6),
    79: (2, 6),
    207: (2, 6),
    86: (3, 6),
    118: (3, 6),
    87: (3, 6),
    119: (3, 6),
    216: (4, 6),
    220: (4, 6),
    217: (4, 6),
    221: (4, 6),
    120: (5, 6),
    124: (5, 6),
    121: (5, 6),
    125: (5, 6),
    91: (0, 7),
    94: (1, 7),
    122: (2, 7),
    218: (3, 7),
    126: (4, 7),
    219: (5, 7),
}


@dataclasses.dataclass(frozen=True)
class Tileset:
    tileset_surfaces: tuple[pygame.Surface]
    tile_size: int
    invalid_color: pygame.Color
    animation_10: PaletteAnimation
    animation_11: PaletteAnimation
    terrains: dict[TileType, Terrain]
    minimap_color: TileType
    underwater: bool

    def get_terrain(self, tile_type: TileType) -> Terrain:
        return self.terrains[tile_type]

    def __getitem__(self, position: tuple[tuple[int, int], int]) -> pygame.Surface:
        (x, y), v = position
        if self.is_valid(position):
            return self.tileset_surfaces[v].subsurface(
                (x * self.tile_size, y * self.tile_size),
                (self.tile_size, self.tile_size),
            )
        return self.tileset_surfaces[0].subsurface(
            (x * self.tile_size, y * self.tile_size),
            (self.tile_size, self.tile_size),
        )

    def get_tile_position(
        self,
        tile_type: TileType,
        mask: int,
        variation: int = 0,
    ) -> tuple[tuple[int, int], int]:
        return (self.get_position(tile_type, mask), variation)

    def get_position(self, tile_type: TileType, mask: int) -> tuple[int, int]:
        x, y = tile_masks[mask]
        return (x + 6 * tile_type.value, y)

    def get_border_tile(self) -> pygame.Surface:
        return self[(1, 1), 0]

    def is_valid(self, position: tuple[tuple[int, int], int]) -> bool:
        (x, y), v = position
        if v == 0:
            return True
        topleft = (x * self.tile_size, y * self.tile_size)
        return self.tileset_surfaces[v].get_at(topleft) != self.invalid_color

    def update(self):
        if self.animation_10 is not None:
            self.animation_10.update()
            for surf in self.tileset_surfaces:
                self.animation_10.set_palette(surf, 10)

        if self.animation_11 is not None:
            self.animation_11.update()
            for surf in self.tileset_surfaces:
                self.animation_11.set_palette(surf, 11)
