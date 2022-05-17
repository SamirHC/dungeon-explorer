import dataclasses
import os
import pygame
import pygame.image
import xml.etree.ElementTree as ET


base_dir = os.path.join("assets", "images", "MoveAnimations")

@dataclasses.dataclass
class AnimData:
    sheet: pygame.Surface
    size: tuple[int, int]
    durations: tuple[int]
    
    def get_frame(self, index: int) -> pygame.Surface:
        return self.sheet.subsurface((index*self.size[0], 0), self.size)

def get_stat_change_anim_data() -> dict[tuple[str, str], AnimData]:
    res = {}
    stat_change_dir = os.path.join(base_dir, "Stat Change")
    for stat_name in os.listdir(stat_change_dir):
        stat_dir = os.path.join(stat_change_dir, stat_name)
        for anim_type in os.listdir(stat_dir):
            anim_dir = os.path.join(stat_dir, anim_type)
            sheet = pygame.image.load(os.path.join(anim_dir, "new.png"))
            metadata = ET.parse(os.path.join(anim_dir, "metadata.xml")).getroot()
            size_el = metadata.find("Size")
            size = int(size_el.get("width")), int(size_el.get("height"))
            durations = [2]*(sheet.get_width() // size[0])
            res[stat_name, anim_type] = AnimData(sheet, size, durations)
    return res

stat_change_anim_data = get_stat_change_anim_data()
