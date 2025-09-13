import os

import pygame.image

from app.common.constants import IMAGES_DIRECTORY
import app.db.dungeon_data as dungeon_data_db
from app.pokemon.party import Party
from app.scenes.dungeon import FloorTransitionScene
from app.scenes.scene import Scene
from app.pokemon.animation_id import AnimationId
from app.gui import text
from app.gui.frame import Frame
from app.item.inventory import Inventory


class StartDungeonScene(Scene):
    def __init__(self, dungeon_id: int, party: Party, inventory: Inventory):
        super().__init__(30, 30)
        self.dungeon_id = dungeon_id
        self.party = party
        self.inventory = inventory

        self.party.leader.sprite.set_animation_id(AnimationId.IDLE, reset=True)
        self.dungeon_data = dungeon_data_db.load(self.dungeon_id)

        # TODO: Play bg music
        # TODO: Implement sprite walk to dungeon pin on map
        map_bg_path = os.path.join(IMAGES_DIRECTORY, "bg", "system", "S01P01A_layer1.png")
        self.map_bg = pygame.image.load(map_bg_path)
        self.title_surface = self.get_title_surface()

        self.frames_until_next_scene = 120

    def get_title_surface(self) -> pygame.Surface:
        title = text.TextBuilder.build_color(
            text.BROWN, self.dungeon_data.name
        ).render()
        surface = Frame((21, 4))
        rect = title.get_rect(center=surface.get_rect().center)
        surface.blit(title, rect.topleft)
        return surface

    def update(self):
        super().update()
        if self.in_transition:
            return
        self.frames_until_next_scene -= 1
        if self.frames_until_next_scene == 0:
            self.next_scene = FloorTransitionScene(
                self.dungeon_data, 1, self.party, self.inventory
            )

    def render(self):
        surface = super().render()
        surface.blit(self.map_bg, (0, 0))
        surface.blit(self.title_surface, (80, 148))
        surface.blit(self.party.leader.render(), (100, 100))
        return surface
