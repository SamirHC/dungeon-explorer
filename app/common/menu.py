import pygame
import pygame.image
from app.common import settings, inputstream, text
from app.model import frame
from app.db import pointer_animation, pointer_surface


class MenuModel:
    def __init__(self, options: list[str]):
        self.options = options
        self.pointer = 0

    def next(self):
        self.pointer = (self.pointer + 1) % len(self.options)

    def prev(self):
        self.pointer = (self.pointer - 1) % len(self.options)

    @property
    def current_option(self) -> str:
        return self.options[self.pointer]


class PagedMenuModel(MenuModel):
    def __init__(self, pages: list[list[str]]):
        self.page = 0
        self.pages = pages
        super().__init__(self.pages[self.page])

    def next_page(self):
        self.page = (self.page + 1) % len(self.pages)
        self.options = self.pages[self.page]
        self.pointer = 0

    def prev_page(self):
        self.page = (self.page - 1) % len(self.pages)
        self.options = self.pages[self.page]
        self.pointer = 0


class Menu:
    def __init__(self, size: tuple[int, int], options: list[str], alpha=255):
        self.textbox_frame = frame.Frame(size, alpha)
        self.menu = MenuModel(options)
        self.active = [True for _ in options]

    @property
    def pointer(self) -> int:
        return self.menu.pointer
    @pointer.setter
    def pointer(self, value: int):
        self.menu.pointer = value

    @property
    def current_option(self) -> str:
        return self.menu.current_option

    @property
    def is_active_option(self) -> bool:
        return self.active[self.pointer]

    def next(self):
        pointer_animation.restart()
        self.menu.next()

    def prev(self):
        pointer_animation.restart()
        self.menu.prev()

    def process_input(self, input_stream: inputstream.InputStream):
        if input_stream.keyboard.is_pressed(settings.get_option_scroll_down_key()):
            self.next()
        elif input_stream.keyboard.is_pressed(settings.get_option_scroll_up_key()):
            self.prev()

    def update(self):
        pointer_animation.update()
    
    def render(self) -> pygame.Surface:
        surface = self.textbox_frame.copy()
        x, y = self.textbox_frame.container_rect.topleft
        y += 2
        dx = pointer_surface.get_width() + 1
        dy = pointer_surface.get_height() + 2
        for i, option in enumerate(self.menu.options):
            if i == self.menu.pointer:
                surface.blit(pointer_animation.render(), (x, y))
            color = text.WHITE if self.active[i] else text.RED
            text_surface = (
                text.TextBuilder()
                .set_shadow(True)
                .set_color(color)
                .write(option)
                .build()
                .render()
            )
            surface.blit(text_surface, (x + dx, y))
            y += dy
        
        return surface
