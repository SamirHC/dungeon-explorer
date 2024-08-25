from app.common.direction import Direction
from app.pokemon.shadow_size import ShadowSize
from app.pokemon.animation_id import AnimationId
from app.gui.sprite_sheet import SpriteSheet


import pygame


import dataclasses


@dataclasses.dataclass(frozen=True)
class SpriteCollection:
    sprite_sheets: dict[AnimationId, SpriteSheet]
    shadow_size: ShadowSize

    def get_sprite(
        self, anim_id: AnimationId, direction: Direction, index: int
    ) -> pygame.Surface:
        sheet = self.sprite_sheets[anim_id]
        return sheet.get_sprite(direction, index)
