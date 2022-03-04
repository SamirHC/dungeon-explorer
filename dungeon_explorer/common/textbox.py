import os

import pygame
import pygame.image
from dungeon_explorer.common import animation, constants, settings, text


class TextBoxFrame(pygame.Surface):

    # Size: given in terms of number of blocks instead of pixels (where each block is 8x8 pixels)
    # Variation: Different styles to choose from [0,4]
    def __init__(self, size: tuple[int, int]):
        w, h = size
        super().__init__((w*8, h*8), pygame.SRCALPHA)
        variation = settings.get_frame()

        file = os.path.join("assets", "images", "misc",
                            f"FONT_frame{variation}.png")
        self.frame_components = pygame.image.load(file)
        self.frame_components.set_colorkey(self.frame_components.get_at((0, 0)))
        topleft = (0, 0)
        top = (1, 0)
        topright = (2, 0)
        left = (0, 1)
        right = (2, 1)
        bottomleft = (0, 2)
        bottom = (1, 2)
        bottomright = (2, 2)

        self.blit(self.get_component(*topleft), (0, 0))
        self.blit(self.get_component(*topright), ((w-1)*8, 0))
        self.blit(self.get_component(*bottomleft), (0, (h-1)*8))
        self.blit(self.get_component(*bottomright), ((w-1)*8, (h-1)*8))

        for i in range(1, w-1):
            self.blit(self.get_component(*top), (i*8, 0))
            self.blit(self.get_component(*bottom), (i*8, (h-1)*8))

        for j in range(1, h-1):
            self.blit(self.get_component(*left), (0, j*8))
            self.blit(self.get_component(*right), ((w-1)*8, j*8))

        bg = pygame.Surface(((w-2)*8+2, (h-2)*8+2), pygame.SRCALPHA)
        bg.set_alpha(128)
        bg.fill(constants.BLACK)
        self.blit(bg, (7, 7))

    def get_component(self, x, y):
        return self.frame_components.subsurface((x*8, y*8), (8, 8))


class MenuOption:
    def __init__(self, size: tuple[int, int], name: str, active_color: pygame.Color=constants.WHITE):
        self.size = size
        self.name = name
        self.active_color = active_color
        self.is_active = True

    def deactivate(self):
        self.is_active = False

    def render(self):
        surface = pygame.Surface(self.size, pygame.SRCALPHA)
        surface.blit(text.build(self.name, self.active_color if self.is_active else constants.RED), (0, 0))
        return surface


class Menu:
    POINTER_FILE = os.path.join("assets", "images", "misc", "pointer.png")

    def __init__(self, size: tuple[int, int], options: list[str]):
        self.pointer_surface = pygame.image.load(Menu.POINTER_FILE)
        self.pointer_surface.set_colorkey(self.pointer_surface.get_at((0, 0)))
        self.textbox_frame = TextBoxFrame(size)
        self.options = [MenuOption((50, 13), op) for op in options]
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
        self.contents: list[pygame.Surface] = []
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
        for i, text_surface in enumerate(self.contents):
            x = x_gap
            y = y_gap + spacing * i
            self.surface.blit(text_surface, (x, y))

    def append(self, text_surface):
        self.contents.append(text_surface)


class TextLog:
    T = 12
    def __init__(self, size: tuple[int, int]):
        self.size = size
        self.contents: list[pygame.Surface] = []
        self.frame = TextBoxFrame(size)
        self.index = 0
        self.is_active = False

    def append(self, text_surface: pygame.Surface):
        self.contents.append(text_surface)
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

