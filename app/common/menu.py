import pygame
import pygame.image
from app.common.action import Action
from app.common.inputstream import InputStream
from app.common import settings
from app.gui.frame import Frame
import app.db.database as db
from app.gui import text


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
        self.textbox_frame = Frame(size, alpha)
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
        db.pointer_animation.restart()
        self.menu.next()

    def prev(self):
        db.pointer_animation.restart()
        self.menu.prev()

    def process_input(self, input_stream: InputStream):
        kb = input_stream.keyboard
        if kb.is_pressed(settings.get_key(Action.DOWN)):
            self.next()
        elif kb.is_pressed(settings.get_key(Action.UP)):
            self.prev()

    def update(self):
        db.pointer_animation.update()

    def render(self) -> pygame.Surface:
        surface = self.textbox_frame.copy()
        x, y = self.textbox_frame.container_rect.topleft
        y += 2
        dx = db.pointer_surface.get_width() + 1
        dy = db.pointer_surface.get_height() + 2
        for i, option in enumerate(self.menu.options):
            if i == self.menu.pointer:
                surface.blit(db.pointer_animation.get_current_frame(), (x, y))
            color = text.WHITE if self.active[i] else text.RED
            surface.blit(self.render_option(option, color), (x + dx, y))
            y += dy

        return surface

    def render_option(self, option, color) -> pygame.Surface:
        return text.TextBuilder.build_color(color, option).render()
