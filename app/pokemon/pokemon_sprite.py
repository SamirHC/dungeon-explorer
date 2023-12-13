
import pygame
from app.common.direction import Direction
from app.pokemon.animation_id import AnimationId
from app.pokemon.sprite_collection import SpriteCollection
from app.pokemon.sprite_sheet import SpriteSheet


class PokemonSprite:
    def __init__(self, sprite_collection: SpriteCollection):
        self.sprite_collection = sprite_collection
        self.direction = Direction.SOUTH
        self.animation_id = AnimationId.IDLE
        self.reset_to = AnimationId.IDLE
        self.shadow_size = self.sprite_collection.shadow_size
        self.timer = 0
        self.index = 0

    def set_direction(self, d: Direction):
        if d is not self.direction:
            self.direction = d
            self.animation_id = self.reset_to
            self.timer = 0
            self.index = 0

    def set_animation_id(self, anim_id: AnimationId):
        if anim_id is not self.animation_id:
            self.animation_id = anim_id
            self.timer = 0
            self.index = 0

    @property
    def current_sheet(self) -> SpriteSheet:
        return self.sprite_collection.sprite_sheets[self.animation_id.value]

    @property
    def current_shadow_position(self) -> tuple[int, int]:
        return self.current_sheet.get_shadow_position(self.direction, self.index)

    """
    @property
    def current_red_offset_position(self) -> tuple[int, int]:
        return self.current_sheet.get_offset_position((255, 0, 0, 255), self.direction, self.index)
    
    @property
    def current_green_offset_position(self) -> tuple[int, int]:
        return self.current_sheet.get_offset_position((0, 255, 0, 255), self.direction, self.index)
    
    @property
    def current_blue_offset_position(self) -> tuple[int, int]:
        return self.current_sheet.get_offset_position((0, 0, 255, 255), self.direction, self.index)
    
    @property
    def current_black_offset_position(self) -> tuple[int, int]:
        return self.current_sheet.get_offset_position((0, 0, 0, 255), self.direction, self.index)
    """

    def update(self):
        self.timer += 1
        if self.timer < self.current_sheet.durations[self.index]:
            return
        self.timer = 0
        self.index += 1
        if self.index == len(self.current_sheet):
            self.animation_id = self.reset_to
            self.index = 0

    def render(self) -> pygame.Surface:
        return self.current_sheet.get_sprite(self.direction, self.index)
