
import pygame
from app.common.direction import Direction
from app.pokemon.SpriteCollection import SpriteCollection
from app.pokemon.sprite_sheet import SpriteSheet


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
    def shadow_size(self):
        return self.sprite_collection.shadow_size

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
