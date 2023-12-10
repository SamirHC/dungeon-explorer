import dataclasses

import pygame
from app.common.direction import Direction
from app.pokemon import shadow
from app.dungeon.color_map import ColorMap


@dataclasses.dataclass
class SpriteSheet:
    name: str
    sheet: pygame.Surface
    sprite_size: tuple[int, int]
    durations: tuple[int]
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

    def with_colormap(self, col_map: ColorMap):
        return SpriteSheet(
            self.name,
            col_map.transform_surface_colors(self.sheet, self.colors),
            self.sprite_size,
            self.durations,
            self.colors,
        )


@dataclasses.dataclass(frozen=True)
class SpriteCollection:
    sprite_sheets: dict[int, SpriteSheet]
    shadow_size: shadow.ShadowSize

    def get_sprite(
        self, anim_id: int, direction: Direction, index: int
    ) -> pygame.Surface:
        sheet = self.sprite_sheets[anim_id]
        return sheet.get_sprite(direction, index)

    def with_colormap(self, col_map: ColorMap):
        return SpriteCollection(
            {
                i: sheet.with_colormap(col_map)
                for i, sheet in self.sprite_sheets.items()
            },
            self.shadow_size,
        )


class PokemonSprite:
    WALK_ANIMATION_ID = 0
    SLEEP_ANIMATION_ID = 5
    HURT_ANIMATION_ID = 6
    IDLE_ANIMATION_ID = 7

    def __init__(self, sprite_collection: SpriteCollection):
        self.sprite_collection = sprite_collection
        self._direction = Direction.SOUTH
        self._animation_id = self.IDLE_ANIMATION_ID
        self.timer = 0
        self.index = 0
        self.update_current_sprite()
        self.reset_to = self.IDLE_ANIMATION_ID

    @property
    def direction(self) -> Direction:
        return self._direction

    @direction.setter
    def direction(self, new_direction):
        if self.direction is new_direction:
            return
        self._direction = new_direction
        self.animation_id = self.reset_to
        self.timer = 0
        self.index = 0
        self.update_current_sprite()

    @property
    def animation_id(self) -> int:
        return self._animation_id

    @animation_id.setter
    def animation_id(self, new_anim_id: int):
        if new_anim_id == self._animation_id:
            return
        self._animation_id = new_anim_id
        self.timer = 0
        self.index = 0
        self.update_current_sprite()

    @property
    def current_sheet(self) -> SpriteSheet:
        return self.sprite_collection.sprite_sheets[self.animation_id]

    def update_current_sprite(self):
        self.sprite_surface = self.current_sheet.get_sprite(self.direction, self.index)

    def update(self):
        self.timer += 1
        if self.timer < self.current_sheet.durations[self.index]:
            return
        self.timer = 0
        self.index += 1
        if self.index == len(self.current_sheet):
            self.animation_id = self.reset_to
            self.index = 0
        self.update_current_sprite()

    def render(self) -> pygame.Surface:
        return self.sprite_surface
