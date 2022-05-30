import dataclasses
import pygame


@dataclasses.dataclass
class GroundData:
    bg: pygame.Surface
    collision: set[tuple[int, int]]
    spawn: tuple[int, int]


class Ground:
    def __init__(self, ground_data: GroundData):
        self.ground_data = ground_data

    def render(self) -> pygame.Surface:
        return self.ground_data.bg.copy()