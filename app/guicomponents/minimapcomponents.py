import os

import pygame

class MiniMapComponents:
    SIZE = 4

    def __getitem__(self, position: tuple[int, int]) -> pygame.Surface:
        x, y = position
        return self.components.subsurface((x*self.SIZE, y*self.SIZE), (self.SIZE, self.SIZE))   

    def __init__(self, variation: int, color: pygame.Color):
        self.color = color

        file = os.path.join("assets", "images", "minimap", f"minimap{variation}.png")
        self.components = pygame.image.load(file)
        self.components.set_colorkey(self.components.get_at((0, 0)))

        mask_cardinal_values = [
            15, 14, 13, 12, 7, 6, 5, 4,
            11, 10,  9,  8, 3, 2, 1, 0
        ]
        self.masks_to_position = {m: (i % 8, i // 8) for i, m in enumerate(mask_cardinal_values)}

        self.enemy = self[2, 0]
        self.item = self[3, 0]
        self.trap = self[4, 0]
        self.warp_zone = self[5, 0]
        self.stairs = self[6, 0]
        self.wonder_tile = self[7, 0]
        self.user = self[0, 1]
        self.ally = self[2, 1]
        self.hidden_stairs = self[5, 1]

        self.filled_ground = {}
        offset = 2
        for k, (x, y) in self.masks_to_position.items():
            surface = self[x, y+offset]
            surface.set_palette_at(7, self.color)
            self.filled_ground[k] = surface
        
        self.unfilled_ground = {}
        offset = 4
        for k, (x, y) in self.masks_to_position.items():
            surface = self[x, y+offset]
            surface.set_palette_at(7, self.color)
            self.unfilled_ground[k] = surface
    
    def get_ground(self, cardinal_mask: int, is_filled: bool = True) -> pygame.Surface:
        image_dict = self.filled_ground if is_filled else self.unfilled_ground
        return image_dict[cardinal_mask]

