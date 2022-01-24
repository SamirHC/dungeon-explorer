import constants
import pokemon
import pygame


class Camera:
    def __init__(self, target: pokemon.Pokemon):
        self.target = target

    @property
    def size(self) -> tuple[int, int]:
        return constants.DISPLAY_SIZE

    @property
    def position(self) -> tuple[int, int]:
        return (self.x, self.y)

    @property
    def x(self) -> int:
        return (self.target.grid_pos[0] - 5) * constants.TILE_SIZE + self.offset[0]

    @property
    def y(self) -> int:
        return (self.target.grid_pos[1] - 4) * constants.TILE_SIZE + self.offset[1]

    @property
    def offset(self) -> tuple[int, int]:
        return (4, 4)

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.position, self.size)