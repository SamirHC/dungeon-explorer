import xml.etree.ElementTree as ET
import os
import pygame
import csv
from app.common.action import Action
from app.common.inputstream import InputStream
from app.common import menu, constants, text, settings
from app.model.frame import Frame

from app.common.constants import USERDATA_DIRECTORY, GAMEDATA_DIRECTORY


class DestinationMenu:
    def __init__(self):
        root = ET.parse(os.path.join(USERDATA_DIRECTORY, "destinations.xml")).getroot()
        self.dungeon_list = [int(d.get("id")) for d in root.findall("Dungeon") if int(d.get("unlocked"))]
        pages = [[]]
        dungeon_root = os.path.join(GAMEDATA_DIRECTORY, "dungeons", "dungeons.csv")
        for dungeon_id in self.dungeon_list:
            with open(dungeon_root, newline="") as dungeons_file:
                reader = csv.DictReader(dungeons_file)
                for i, row in enumerate(reader):
                    if len(pages[-1]) == 8:
                        pages.append([])
                    if i == dungeon_id:
                        name = row["Name"]
                        pages[-1].append(name)
        self.model = menu.PagedMenuModel(pages)
        self.frame = Frame((18, 20)).with_header_divider().with_footer_divider()
        self.dungeon_id: int = None
        self.cancelled = False

    def process_input(self, input_stream: InputStream):
        kb = input_stream.keyboard
        if kb.is_pressed(settings.get_key(Action.DOWN)):
            menu.pointer_animation.restart()
            self.model.next()
        elif kb.is_pressed(settings.get_key(Action.UP)):
            menu.pointer_animation.restart()
            self.model.prev()
        elif kb.is_pressed(settings.get_key(Action.RIGHT)):
            menu.pointer_animation.restart()
            self.model.next_page()
        elif kb.is_pressed(settings.get_key(Action.LEFT)):
            menu.pointer_animation.restart()
            self.model.prev_page()
        elif kb.is_pressed(settings.get_key(Action.INTERACT)):
            self.dungeon_id = self.dungeon_list[self.model.page*8 + self.model.pointer]

    def update(self):
        menu.pointer_animation.update()
    
    def render(self) -> pygame.Surface:
        surface = pygame.Surface(constants.DISPLAY_SIZE, pygame.SRCALPHA)
        frame = self.frame.copy()
        title_surface = (
            text.TextBuilder()
            .set_shadow(True)
            .set_color(text.WHITE)
            .write("  Destination")
            .build()
            .render()
        )
        x, y = 8, 8
        frame.blit(title_surface, (x, y))
        end = pygame.Vector2(frame.get_width()-8, 8)
        page_surface = (
            text.TextBuilder()
            .set_shadow(True)
            .set_color(text.WHITE)
            .write(f"({self.model.page + 1}/{len(self.model.pages)})")
            .build()
            .render()
        )
        page_num_rect = page_surface.get_rect(topright=end)
        frame.blit(page_surface, page_num_rect.topleft)
        x += 26
        y += 18
        for name in self.model.pages[self.model.page]:
            name_surface = (
                text.TextBuilder()
                .set_shadow(True)
                .set_color(text.BROWN)
                .write(name)
                .build()
                .render()
            )
            frame.blit(name_surface, (x, y))
            y += 14
        pointer_position = pygame.Vector2(0, 14)*self.model.pointer + self.frame.container_rect.topleft + (0, 18)
        frame.blit(menu.pointer_animation.render(), pointer_position)
        surface.blit(frame, (8, 8))
        return surface