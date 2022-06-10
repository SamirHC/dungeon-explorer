import xml.etree.ElementTree as ET
import os
import pygame
from dungeon_explorer.common import inputstream, menu, frame, constants, text


class DestinationMenu:
    def __init__(self):
        root = ET.parse(os.path.join("data", "userdata", "destinations.xml")).getroot()
        self.dungeon_list = [int(d.get("id")) for d in root.findall("Dungeon") if int(d.get("unlocked"))]
        pages = [[]]
        for dungeon_id in self.dungeon_list:
            if len(pages[-1]) == 8:
                pages.append([])
            dungeon_root = ET.parse(os.path.join("data", "gamedata", "dungeons", str(dungeon_id), f"dungeon_data{dungeon_id}.xml")).getroot()
            name = dungeon_root.find("Name").text
            pages[-1].append(name)
        self.model = menu.PagedMenuModel(pages)
        self.frame = frame.Frame((18, 20)).with_header_divider().with_footer_divider()
        self.dungeon_id: int = None
        self.cancelled = False

    def process_input(self, input_stream: inputstream.InputStream):
        kb = input_stream.keyboard
        if kb.is_pressed(pygame.K_s):
            menu.pointer_animation.restart()
            self.model.next()
        elif kb.is_pressed(pygame.K_w):
            menu.pointer_animation.restart()
            self.model.prev()
        elif kb.is_pressed(pygame.K_d):
            menu.pointer_animation.restart()
            self.model.next_page()
        elif kb.is_pressed(pygame.K_a):
            menu.pointer_animation.restart()
            self.model.prev_page()
        elif kb.is_pressed(pygame.K_RETURN):
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