from app.common.direction import Direction
from app.dungeon.color_map import ColorMap
from app.pokemon import shadow
from app.pokemon.sprite_sheet import SpriteSheet


import pygame


import dataclasses


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
