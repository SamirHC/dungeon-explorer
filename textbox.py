import constants
import os
import text
import pygame
import pygame.constants
import pygame.image


class TextBoxFrame(pygame.Surface):

    # Dimensions are given in terms of number of blocks instead of pixels (where each block is 8x8 pixels)
    def __init__(self, dimensions: tuple[int, int]):
        w, h = dimensions
        super().__init__((w * 8, h * 8), pygame.constants.SRCALPHA)

        variation = 0  # Different styles to choose from [0,4]
        file = os.path.join(os.getcwd(), "assets", "misc",
                            f"FONT_frame{variation}.png")
        frame_components = pygame.image.load(file)
        frame_components.set_colorkey(frame_components.get_at((0, 0)))
        topleft = frame_components.subsurface(pygame.Rect(0, 0, 8, 8))
        top = frame_components.subsurface(pygame.Rect(1*8, 0, 8, 8))
        topright = frame_components.subsurface(pygame.Rect(2*8, 0, 8, 8))
        left = frame_components.subsurface(pygame.Rect(0, 1*8, 8, 8))
        right = frame_components.subsurface(pygame.Rect(2*8, 1*8, 8, 8))
        bottomleft = frame_components.subsurface(pygame.Rect(0, 2*8, 8, 8))
        bottom = frame_components.subsurface(pygame.Rect(1*8, 2*8, 8, 8))
        bottomright = frame_components.subsurface(pygame.Rect(2*8, 2*8, 8, 8))

        self.blit(topleft, (0, 0))
        self.blit(topright, ((w-1)*8, 0))
        self.blit(bottomleft, (0, (h-1)*8))
        self.blit(bottomright, ((w-1)*8, (h-1)*8))

        for i in range(1, w-1):
            self.blit(top, (i*8, 0))
            self.blit(bottom, (i*8, (h-1)*8))

        for j in range(1, h-1):
            self.blit(left, (0, j*8))
            self.blit(right, ((w-1)*8, j*8))

        bg = pygame.Surface(((w-2)*8+2, (h-2)*8+2), pygame.constants.SRCALPHA)
        bg.set_alpha(128)
        bg.fill(constants.BLACK)
        self.blit(bg, (7, 7))


class MenuOption(pygame.Surface):
    def __init__(self, size: tuple[int, int], name: str):
        super().__init__(size)
        self.name = name


class Menu(TextBoxFrame):
    def __init__(self, size: tuple[int, int], options: list[MenuOption]):
        super().__init__(size)
        self.options = options


class TextBox:
    def __init__(self, dimensions: tuple[int, int], max_lines: int):
        self.dimensions = dimensions
        self.max_lines = max_lines
        self.contents: list[text.Text] = []
        self.surface = self.draw()

    def draw(self) -> pygame.Surface:
        self.surface = TextBoxFrame(self.dimensions)
        self.draw_contents()
        return self.surface

    def draw_contents(self):
        x_gap = 10
        y_gap = 7
        spacing = 14
        i = 0
        while len(self.contents) > self.max_lines:
            self.contents.pop(0)
        for i, content in enumerate(self.contents):
            x = x_gap
            y = y_gap + spacing * i
            image = content.surface
            self.surface.blit(image, (x, y))

    def append(self, text: text.Text):
        self.contents.append(text)


message_log = TextBox((30, 7), 3)
