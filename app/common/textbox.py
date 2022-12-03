import pygame
import pygame.draw
import pygame.image
from app.common import text, frame


class TextBox:
    def __init__(self, size: tuple[int, int], max_lines: int):
        self.size = size
        self.max_lines = max_lines
        self.frame = frame.Frame(self.size, 128)
        self.contents: list[pygame.Surface] = []
        self.surface = self.draw()

    def draw(self) -> pygame.Surface:
        self.surface = pygame.Surface(self.frame.get_size(), pygame.SRCALPHA)
        self.surface.blit(self.frame, (0, 0))
        self.draw_contents()
        return self.surface

    def draw_contents(self):
        x, y = 12, 10
        while len(self.contents) > self.max_lines:
            self.contents.pop(0)
        for item in self.contents:
            self.surface.blit(item, (x, y))
            y += item.get_height()

    def append(self, item):
        self.contents.append(item)


class DungeonTextBox:
    def __init__(self):
        self.frame = frame.Frame((30, 7), 128)
        self.VISIBILITY_DURATION = 200
        self.restart()

    @property
    def is_visible(self) -> bool:
        return self.visibility_timer > 0

    def restart(self):
        self.display_area = pygame.Rect((0, 0), self.frame.container_rect.size)
        self.height = 0
        self.content_surface = pygame.Surface((self.display_area.w, self.height), pygame.SRCALPHA)
        self.t = 0
        self.visibility_timer = 0

    def write(self, message_surface: pygame.Surface):
        self.visibility_timer = self.VISIBILITY_DURATION
        self.height += message_surface.get_height()
        if self.height > self.display_area.h:
            self.t += message_surface.get_height()
        new_content_surface = pygame.Surface((self.content_surface.get_width(), self.height), pygame.SRCALPHA)
        new_content_surface.blit(self.content_surface, (0, 0))
        new_content_surface.blit(message_surface, (0, self.content_surface.get_height()))
        self.content_surface = new_content_surface
    
    def new_divider(self):
        self.content_surface.blit(text.divider(self.display_area.w), (0, self.height - 2))
    
    def update(self):
        if self.t != 0:
            self.t -= 1
            self.display_area.y += 1
        if self.is_visible != 0:
            self.visibility_timer -= 1
            if self.visibility_timer == 0:
                self.restart()
        
    def render(self) -> pygame.Surface:
        if self.is_visible:
            surface = self.frame.copy()
            surface.blit(self.content_surface, (12, 10), area=self.display_area)
            return surface
        else:
            return pygame.Surface((0, 0))


class TextLog:
    def __init__(self, size: tuple[int, int]):
        self.size = size
        self.frame = frame.Frame(size)
        self.cursor = 0, 0
        self.canvas = pygame.Surface((self.canvas_width, self.canvas_height), pygame.SRCALPHA)

    @property
    def canvas_topleft(self) -> tuple[int, int]:
        return 12, 10
    
    @property
    def canvas_topright(self) -> tuple[int, int]:
        x, y = self.size
        x *= 8
        y *= 8
        dx, dy = self.canvas_topleft
        return x - dx, y - dy

    @property
    def canvas_width(self):
        return self.canvas_topright[0] - self.canvas_topleft[0]

    @property
    def canvas_height(self):
        return self.size[1] * 8 - 20

    def write(self, message: str, color: pygame.Color):
        words = message.split(" ")
        for word in words:
            text_surface = (
                text.TextBuilder()
                .set_shadow(True)
                .set_color(color)
                .write(f"{word} ")
                .build()
                .render()
            )
            if self.canvas.get_width() < self.cursor[0] + text_surface.get_width():
                self.cursor = 0, self.cursor[1] + 14
            self.canvas.blit(text_surface, self.cursor)
            self.cursor = self.cursor[0] + text_surface.get_width(), self.cursor[1]
    
    def write_multicolor(self, items: tuple[str, pygame.Color]):
        for item in items:
            self.write(item[0], item[1])

    def write_line(self, items: tuple[str, pygame.Color]):
        self.write_multicolor(items)
        self.cursor = 0, self.cursor[1] + 14
        self.canvas.blit(text.divider(self.canvas_width), self.cursor)
        self.cursor = 0, self.cursor[1] + 2

    def render(self):
        surface = self.frame
        surface.blit(self.canvas, self.canvas_topleft)
        return surface