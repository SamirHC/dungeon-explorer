import pygame
from app.gui import text
from app.gui.frame import Frame


class TextBox:
    def __init__(self, size: tuple[int, int], max_lines: int):
        self.size = size
        self.max_lines = max_lines
        self.frame = Frame(self.size, 128)
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
    VISIBILITY_DURATION = 200

    def __init__(self):
        self.frame = Frame((30, 7), 128)
        self.restart()

    @property
    def is_visible(self) -> bool:
        return self.visibility_timer > 0

    def restart(self):
        self.display_area = pygame.Rect((0, 0), self.frame.container_rect.size)
        self.height = 0
        self.content_surface = pygame.Surface(
            (self.display_area.w, self.height), pygame.SRCALPHA
        )
        self.t = 0
        self.visibility_timer = 0

    def write(self, message_surface: pygame.Surface):
        self.visibility_timer = self.VISIBILITY_DURATION
        self.height += message_surface.get_height()
        if self.height > self.display_area.h:
            self.t += message_surface.get_height()
        new_content_surface = pygame.Surface(
            (self.content_surface.get_width(), self.height), pygame.SRCALPHA
        )
        new_content_surface.blit(self.content_surface, (0, 0))
        new_content_surface.blit(
            message_surface, (0, self.content_surface.get_height())
        )
        self.content_surface = new_content_surface

    def new_divider(self):
        self.content_surface.blit(
            text.divider(self.display_area.w), (0, self.height - 2)
        )

    def update(self):
        if self.t != 0:
            self.t -= 1
            self.display_area.y += 1
        if self.is_visible:
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


class MessageList:
    OFFSET_X = 4
    OFFSET_Y = 2
    LINE_H = 13
    LINE_W = 240
    BAR_SURFACE = text.divider(LINE_W - 2 * 8)

    def __init__(self):
        self.lines: list[text.Text] = []
        self.bar_indices: list[int] = []

    @property
    def content_rect(self):
        return pygame.Rect(0, 0, self.LINE_W, len(self.lines) * self.LINE_H)

    def write_line(self, text: text.Text):
        self.lines.append(text)

    def write_bar_line(self, text: text.Text):
        self.bar_indices.append(len(self.lines))
        self.write_line(text)

    def render(self) -> pygame.Surface:
        surface = pygame.Surface(self.content_rect.size, pygame.SRCALPHA)
        surface.blits(
            (line.render(), (self.OFFSET_X, self.OFFSET_Y + i * self.LINE_H))
            for i, line in enumerate(self.lines)
        )
        surface.blits(
            (self.BAR_SURFACE, (0, i * self.LINE_H)) for i in self.bar_indices
        )
        return surface


class DungeonMessageLog:
    NUM_LINES = 9

    def __init__(self):
        self.message_list = MessageList()
        self.frame = Frame((30, 22), 128).with_header_divider().with_footer_divider()
        self.frame.blit(text.TextBuilder.build_white("  Message log").render(), (8, 8))
        # Blit up and down arrows and X in footer.
        # Where to draw message list relative to frame
        self.container_rect = pygame.Rect(
            8,
            8 + 18,
            self.message_list.LINE_W,
            self.NUM_LINES * self.message_list.LINE_H,
        )
        self.cursor = 0

    def scroll_up(self):
        if self.cursor < len(self.message_list.lines) - self.NUM_LINES:
            self.cursor += 1

    def scroll_down(self):
        if self.cursor > 0:
            self.cursor -= 1

    def render(self) -> pygame.Surface:
        surface = self.frame.copy()
        bottom = self.message_list.content_rect.bottom
        message_list_visible_rect = pygame.Rect(
            0,
            max(
                0,
                bottom
                - self.container_rect.height
                - self.cursor * self.message_list.LINE_H,
            ),
            self.message_list.LINE_W,
            min(self.message_list.content_rect.height, self.container_rect.height),
        )
        surface.blit(
            self.message_list.render().subsurface(message_list_visible_rect),
            self.container_rect,
        )
        return surface
