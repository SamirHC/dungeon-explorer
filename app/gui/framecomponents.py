import pygame


class FrameComponents:
    SIZE = 8

    def __init__(self, surface: pygame.Surface):
        self.surface = surface
        self.get_components()

    def __getitem__(self, position: tuple[int, int]):
        x, y = position
        return self.surface.subsurface(
            (x * self.SIZE, y * self.SIZE), (self.SIZE, self.SIZE)
        )

    def get_components(self):
        self.topleft = self[0, 0]
        self.top = self[1, 0]
        self.topright = self[2, 0]
        self.left = self[0, 1]
        self.right = self[2, 1]
        self.bottomleft = self[0, 2]
        self.bottom = self[1, 2]
        self.bottomright = self[2, 2]

        self.portrait_topleft = self[3, 0]
        self.portrait_top = self[4, 0]
        self.portrait_topright = self[5, 0]
        self.portrait_left = self[3, 1]
        self.portrait_right = self[5, 1]
        self.portrait_bottomleft = self[3, 2]
        self.portrait_bottom = self[4, 2]
        self.portrait_bottomright = self[5, 2]
