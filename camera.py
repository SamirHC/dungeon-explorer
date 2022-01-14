import constants
import movementsystem
import pokemon
import pygame


class Camera:
    def __init__(self, target: pokemon.Pokemon, movement_system: movementsystem.MovementSystem):
        self.movement_system = movement_system
        self.target = target

    @property
    def size(self) -> tuple[int, int]:
        return constants.DISPLAY_SIZE

    @property
    def position(self) -> tuple[int, int]:
        return (self.x, self.y)

    @property
    def x(self) -> int:
        return (self.target.grid_pos[0] - 5 - self.movement_offset[0]) * constants.TILE_SIZE + self.offset[0]

    @property
    def y(self) -> int:
        return (self.target.grid_pos[1] - 4 - self.movement_offset[1]) * constants.TILE_SIZE + self.offset[1]

    @property
    def offset(self) -> tuple[int, int]:
        return (4, 4)

    @property
    def movement_offset(self) -> tuple[int, int]:
        if not self.movement_system.is_active:
            return (0, 0)
        else:
            dx, dy = self.target.direction.value
            frac = self.movement_system.motion_time_left / self.movement_system.time_for_one_tile
            return (dx * frac, dy * frac)

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.position, self.size)