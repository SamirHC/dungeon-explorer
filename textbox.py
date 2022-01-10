import constants
import text
import button
import pygame
import pygame.draw


class TextBoxFrame(pygame.Surface):
    BORDER_THICKNESS = 0.2/9.6 * constants.DISPLAY_WIDTH
    BORDER_COLOR = constants.BORDER_BLUE_1

    def __init__(self, position: tuple[int, int]):
        w, h = position
        super().__init__((w, h))
        pygame.draw.rect(self, self.BORDER_COLOR,
                         (0, 0, w, h))
        pygame.draw.rect(self, constants.BLACK, (TextBox.BORDER_THICKNESS, TextBox.BORDER_THICKNESS,
                         w - 2*TextBox.BORDER_THICKNESS, h-2*TextBox.BORDER_THICKNESS))

class TextBox:
    BORDER_THICKNESS = 3

    def __init__(self, rect: pygame.Rect, max_lines: int):
        self.rect = rect
        self.max_lines = max_lines
        self.contents: list[text.Text] = []
        self.surface = self.draw()

    def draw(self):
        self.surface = pygame.Surface((self.rect.w, self.rect.h))
        self.surface.set_alpha(180)
        border_color = constants.BORDER_BLUE_1
        pygame.draw.rect(self.surface, border_color,
                         (0, 0, self.rect.w, self.rect.h))
        pygame.draw.rect(self.surface, constants.BLACK, (TextBox.BORDER_THICKNESS, TextBox.BORDER_THICKNESS,
                         self.rect.w - 2*TextBox.BORDER_THICKNESS, self.rect.h-2*TextBox.BORDER_THICKNESS))
        self.draw_contents()
        return self.surface

    def draw_contents(self):
        x_gap = 5
        y_gap = 5
        spacing = 36
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


message_log = TextBox(pygame.Rect(35, 500, 1210, 200), 5)
