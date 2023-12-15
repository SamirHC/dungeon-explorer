from app.common.direction import Direction
from app.dungeon.color_map import ColorMap


import pygame


import dataclasses


@dataclasses.dataclass
class SpriteSheet:
    name: str
    sheet: pygame.Surface
    sprite_size: tuple[int, int]
    durations: list[int]
    shadow_positions: list[list[tuple[int, int]]]
    offset_positions: dict[tuple[int, int, int, int], list[list[tuple[int, int]]]]
    colors: list[pygame.Color]
    is_singular: bool = dataclasses.field(init=False)
    row_directions: list[Direction] = dataclasses.field(init=False)

    def __post_init__(self):
        self.is_singular = self.sheet.get_height() == self.sprite_size[1]
        self.row_directions = []
        d = Direction.SOUTH
        num_rows = 1 if self.is_singular else 8
        for i in range(num_rows):
            self.row_directions.append(d)
            d = d.anticlockwise()

    def __len__(self):
        return len(self.durations)

    def get_row(self, d: Direction):
        if self.is_singular:
            d = Direction.SOUTH
        return self.row_directions.index(d)

    def get_position(self, d: Direction, index: int) -> tuple[int, int]:
        w, h = self.sprite_size
        x = index * w
        y = self.get_row(d) * h
        return x, y

    def get_sprite(self, d: Direction, index: int) -> pygame.Surface:
        if self.is_singular:
            d = Direction.SOUTH
        pos = self.get_position(d, index)
        return self.sheet.subsurface(pos, self.sprite_size)

    def get_shadow_position(self, d: Direction, index: int) -> tuple[int, int]:
        return self.shadow_positions[self.get_row(d)][index]

    def get_offset_position(
        self, color: tuple[int, int, int, int], d: Direction, index: int
    ) -> tuple[int, int]:
        return self.offset_positions[color][self.get_row(d)][index]

    def with_colormap(self, col_map: ColorMap):
        return SpriteSheet(
            self.name,
            col_map.transform_surface_colors(self.sheet, self.colors),
            self.sprite_size,
            self.durations,
            self.colors,
        )
