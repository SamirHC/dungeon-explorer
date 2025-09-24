from __future__ import annotations

import pygame

from app.common import mixer
from app.common.constants import *
import app.db.database as db
import app.db.sfx as sfx_db
import app.db.font as font_db
from app.gui.text import Align, TextBuilder


class ScrollText:
    def __init__(self, tokens: str, with_sound=False, start_t=0):
        self.with_sound = with_sound
        self.is_paused = False
        self.t = 0
        self.pointer_animations: list[int] = []
        command_map = {
            "A": lambda x: tb.set_alignment(Align(int(x))),
            "C": lambda x: tb.set_color(globals()[x]),  # TODO
            "G": lambda x: tb.set_font(font_db.graphic_font)
            .write([int(x)])
            .set_font(font_db.normal_font),
            "K": lambda x: self.pointer_animations.append(self.t),
        }

        tb = TextBuilder()
        i = 0
        n = len(tokens)
        while i < n:
            token = tokens[i]
            if token == "[":
                i += 1
                j = tokens.index("]", i)
                components = tokens[i:j].split(":", maxsplit=2)
                command = components[0]
                arg = components[1] if len(components) > 1 else None
                command_map[command](arg)
                i = j
                if command == "G":
                    self.t += 1
            else:
                tb.write(token)
                if token != "\n":
                    self.t += 1
            i += 1

        self.t = start_t
        self.text = tb.build()
        self.pointer_animation = db.get_pointer_animation()

    def unpause(self):
        self.is_paused = False
        self.t += 1

    def update(self):
        if self.is_paused:
            self.pointer_animation.update()
        if self.is_done:
            return
        if self.t in self.pointer_animations:
            self.is_paused = True
            return
        self.t += 1
        if self.with_sound and not mixer.misc_sfx_channel.get_busy():
            text_tick_sfx = sfx_db.load("SystemSE", 5)
            mixer.misc_sfx_channel.play(text_tick_sfx)

    def render(self) -> pygame.Surface:
        surface = self.text.canvas.copy()
        for i in range(min(self.t, len(self.text.chars))):
            item = self.text.chars[i]
            pos = self.text.positions[i]
            surface.blit(item, pos)
        if self.t in self.pointer_animations:
            pos = pos[0] + item.get_width(), pos[1]
            item = self.pointer_animation.render()
            surface.blit(item, pos)
        return surface

    def get_rect(self, **kwargs) -> pygame.Rect:
        return self.text.get_rect(**kwargs)

    @property
    def is_done(self) -> bool:
        return self.t >= len(self.text.chars)
