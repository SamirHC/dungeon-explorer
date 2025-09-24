from __future__ import annotations
from typing import Any

import pygame

from app.common.action import Action
from app.common.inputstream import InputStream
from app.common import settings
from app.gui.frame import Frame
import app.db.database as db
from app.gui import text


class MenuOption:
    def __init__(self, label: Any, enabled: bool = True, metadata: dict | None = None):
        self.label = label
        # Menu assigned automatically on MenuPage.add_option call
        self.menu: MenuPage | None = None
        self.child_menu: MenuPage | None = None
        self.enabled = enabled
        self.metadata = metadata or {}

    def set_child_menu(self, child_menu: MenuPage):
        self.child_menu = child_menu
        current = child_menu
        # All of the child's adjacent pages also have their parent configured
        while current.parent_menu is not self.menu:
            current.parent_menu = self.menu
            current = child_menu.next_page or current
    
    def __repr__(self) -> str:
        return f"<MenuOption label={self.label}, enabled={self.enabled}, metadata={self.metadata}>"


class MenuPage:
    def __init__(self, label: Any):
        self.label = label
        self.options: list[MenuOption] = []
        # Parent menu set automatically on MenuOption.set_child_menu call
        self.parent_menu: MenuPage | None = None
        self.prev_page: MenuPage | None = None
        self.next_page: MenuPage | None = None
        self.pointer: int = 0

    @property
    def current_option(self) -> MenuOption:
        return self.options[self.pointer]

    def next(self):
        self.pointer = (self.pointer + 1) % len(self.options)

    def prev(self):
        if len(self.options) <= 1:
            return
        self.pointer = (self.pointer - 1) % len(self.options)
    
    def add_option(self, menu_option: MenuOption):
        menu_option.menu = self
        self.options.append(menu_option)

    @staticmethod
    def connect_pages(*pages: MenuPage):
        for i in range(len(pages) - 1):
            current_page = pages[i]
            next_page = pages[i + 1]
            current_page.next_page = next_page
            next_page.prev_page = current_page

        first, last = pages[0], pages[-1]
        first.prev_page = last
        last.next_page = first

    def __repr__(self) -> str:
        return f"<MenuPage label={self.label}, options={self.options}>"


class MenuController:
    def __init__(self, start: MenuPage):
        self.current_page = start
        self.intent = None

    @property
    def current_option(self) -> MenuOption:
        return self.current_page.current_option

    def next(self):
        self.current_page.next()

    def prev(self):
        self.current_page.prev()
    
    def next_page(self):
        self.current_page = self.current_page.next_page or self.current_page
        
    def prev_page(self):
        self.current_page = self.current_page.prev_page or self.current_page

    def select(self):
        option = self.current_option
        if not option.enabled:
            return
        if option.child_menu:
            self.current_page = option.child_menu
        else:
            self.intent = option.label

    def back(self):
        self.current_page = self.current_page.parent_menu or self.current_page

    def consume_intent(self):
        intent, self.intent = self.intent, None
        return intent


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


class MenuRenderer:
    def __init__(
        self,
        size: tuple[int, int],
        alpha=255,
        header=False,
        footer=False,
        title: text.Text = None,
    ):
        self.textbox_frame = Frame(size, alpha)
        self.header = header
        self.footer = footer
        if header:
            self.textbox_frame.with_header_divider()
            if title:
                self.textbox_frame.blit(title.render(), (8, 8))
        if footer:
            self.textbox_frame.with_footer_divider()
        self.pointer_animation = db.get_pointer_animation()

    def update(self):
        self.pointer_animation.update()

    def render(self, menu_page: MenuPage) -> pygame.Surface:
        surface = self.textbox_frame.copy()
        x, y = self.textbox_frame.container_rect.topleft
        y += 2
        if self.header:
            y += 16
        dx = db.get_pointer().get_width() + 1
        dy = db.get_pointer().get_height() + 2
        for i, option in enumerate(menu_page.options):
            if i == menu_page.pointer:
                surface.blit(self.pointer_animation.get_current_frame(), (x, y))
            surface.blit(self.render_option(option), (x + dx, y))
            y += dy

        return surface

    def render_option(self, option: MenuOption) -> pygame.Surface:
        color = text.WHITE if option.enabled else text.RED
        return text.TextBuilder.build_color(color, option.label).render()





class Menu:
    def __init__(
        self,
        size: tuple[int, int],
        options: list[str],
        alpha=255,
        header=False,
        footer=False,
        title: text.Text = None,
    ):
        self.textbox_frame = Frame(size, alpha)
        self.header = header
        self.footer = footer
        if header:
            self.textbox_frame.with_header_divider()
            if title:
                self.textbox_frame.blit(title.render(), (8, 8))
        if footer:
            self.textbox_frame.with_footer_divider()
        self.menu = MenuModel(options)
        self.active = [True for _ in options]
        self.pointer_animation = db.get_pointer_animation()

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
        self.pointer_animation.restart()
        self.menu.next()

    def prev(self):
        self.pointer_animation.restart()
        self.menu.prev()

    def process_input(self, input_stream: InputStream):
        kb = input_stream.keyboard
        if kb.is_pressed(settings.get_key(Action.DOWN)):
            self.next()
        elif kb.is_pressed(settings.get_key(Action.UP)):
            self.prev()

    def update(self):
        self.pointer_animation.update()

    def render(self) -> pygame.Surface:
        surface = self.textbox_frame.copy()
        x, y = self.textbox_frame.container_rect.topleft
        y += 2
        if self.header:
            y += 16
        dx = db.get_pointer().get_width() + 1
        dy = db.get_pointer().get_height() + 2
        for i, option in enumerate(self.menu.options):
            if i == self.menu.pointer:
                surface.blit(self.pointer_animation.get_current_frame(), (x, y))
            color = text.WHITE if self.active[i] else text.RED
            surface.blit(self.render_option(option, color), (x + dx, y))
            y += dy

        return surface

    def render_option(self, option, color) -> pygame.Surface:
        return text.TextBuilder.build_color(color, option).render()
