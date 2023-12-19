import pygame


class Font:
    CHARS_PER_ROW = 16

    def __init__(self, font_sheet: pygame.Surface, widths: dict[str:int]):
        self.font_sheet = font_sheet
        self.widths = widths
        self.size = self.font_sheet.get_width() // self.CHARS_PER_ROW

        # Optional data for changing colors
        self.editable_palette = None
        self.colorkey = None

    def init(self):
        assert self.is_colorable()
        self.font_sheet.set_colorkey(self.colorkey)

    def __getitem__(self, char: str) -> pygame.Surface:
        char_id = ord(char)
        x = (char_id % self.CHARS_PER_ROW) * self.size
        y = (char_id // self.CHARS_PER_ROW) * self.size
        w, h = self.get_width(char), self.size
        return self.font_sheet.subsurface((x, y, w, h))

    def get_width(self, char: str) -> int:
        char_id = ord(char)
        return self.widths.get(char_id, 0)

    def set_colorable(self, editable_palette: int, colorkey: pygame.Color):
        self.editable_palette = editable_palette
        self.colorkey = colorkey
        return self

    def is_colorable(self) -> bool:
        return self.editable_palette is not None

    @property
    def color(self) -> pygame.Color:
        assert self.is_colorable()
        return self.font_sheet.get_palette_at(self.editable_palette)

    @color.setter
    def color(self, new_color: pygame.Color):
        assert self.is_colorable()
        if new_color != self.colorkey:
            self.font_sheet.set_palette_at(self.editable_palette, new_color)


class GraphicFont:
    def __init__(self, sheet: dict[int, pygame.Surface]):
        self.sheet = sheet
        self.colorkey = pygame.Color(0, 0, 255)
        self.size = 12

    def init(self):
        self.set_colorkey()

    def __getitem__(self, char_id: int) -> pygame.Surface:
        return self.sheet[char_id]

    def get_width(self, char_id: int) -> int:
        return self[char_id].get_width()

    def set_colorkey(self):
        for surf in self.sheet.values():
            surf.set_colorkey(self.colorkey)
