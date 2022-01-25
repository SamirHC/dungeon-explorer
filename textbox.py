from re import T
import animation
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
        file = os.path.join(os.getcwd(), "assets", "images", "misc",
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


class MenuOption:
    def __init__(self, size: tuple[int, int], name: str, active_color: pygame.Color=constants.WHITE):
        self.size = size
        self.name = name
        self.active_color = active_color
        self.is_active = True

    def deactivate(self):
        self.is_active = False

    def render(self):
        surface = pygame.Surface(self.size, pygame.constants.SRCALPHA)
        surface.blit(text.Text(self.name, self.active_color if self.is_active else constants.RED).surface, (0, 0))
        return surface


class Menu:
    POINTER_FILE = os.path.join(os.getcwd(), "assets", "images", "misc", "pointer.png")

    def __init__(self, size: tuple[int, int], options: list[MenuOption]):
        self.pointer_surface = pygame.image.load(Menu.POINTER_FILE)
        self.pointer_surface.set_colorkey(self.pointer_surface.get_at((0, 0)))
        self.textbox_frame = TextBoxFrame(size)
        self.options = options
        self.pointer = 0
        self.pointer_animation = animation.Animation([(self.pointer_surface, 30), (pygame.Surface((0, 0)), 30)])

    def next(self):
        self.pointer_animation.restart()
        self.pointer = (self.pointer + 1) % len(self.options)

    def prev(self):
        self.pointer_animation.restart()
        self.pointer = (self.pointer - 1) % len(self.options)

    def current_option(self) -> MenuOption:
        return self.options[self.pointer]

    def update(self):
        self.pointer_animation.update()
    
    def render(self) -> pygame.Surface:
        x_gap = 8 + self.pointer_surface.get_width()
        y_gap = 10
        spacing = 13
        surface = self.textbox_frame.copy()
        for i, option in enumerate(self.options):
            x = x_gap
            y = y_gap + spacing * i
            surface.blit(option.render(), (x, y))
            if i == self.pointer:
                surface.blit(self.pointer_animation.render(), (8, y))
        return surface


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
        x_gap = 12
        y_gap = 10
        spacing = 13
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


class TextLog:
    T = 12
    def __init__(self, size: tuple[int, int]):
        self.size = size
        self.contents: list[text.Text] = []
        self.frame = TextBoxFrame(size)
        self.index = 0
        self.is_active = False

    def append(self, text: text.Text):
        self.contents.append(text)
        if len(self.contents) > 3:
            self.is_active = True

    def update(self):
        if not self.is_active:
            return
        if not self.timer:
            self.timer = self.T
        self.timer -= 1
        if not self.timer:
            self.is_active = False
            self.index = 0


    def render(self) -> pygame.Surface:
        surface = pygame.Surface(self.frame.get_size(), pygame.SRCALPHA)
        surface.blit(self.frame, (0, 0))
        if not self.is_active:
            pass
        return surface

message_log = TextBox((30, 7), 3)
