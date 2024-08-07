from app.common.constants import IMAGES_DIRECTORY
from app.dungeon.dungeon_data import DungeonData
from app.pokemon.party import Party
from app.scenes.dungeon import FloorTransitionScene
from app.scenes.scene import Scene
from app.pokemon.animation_id import AnimationId
from app.gui import text
from app.gui.frame import Frame

import os
import pygame.image


class StartDungeonScene(Scene):
    def __init__(self, dungeon_id: int, party: Party):
        super().__init__(30, 30)
        self.party = party
        self.party.leader.sprite.set_animation_id(AnimationId.IDLE, True)
        self.dungeon_data = DungeonData(dungeon_id)

        self.map_bg = pygame.image.load(
            os.path.join(IMAGES_DIRECTORY, "bg", "system", "S01P01A_layer1.png")
        )
        self.title_surface = self.get_title_surface()
        self.display_t = 120

    def update(self):
        super().update()
        if self.in_transition:
            return
        self.display_t -= 1
        if self.display_t == 0:
            self.next_scene = FloorTransitionScene(self.dungeon_data, 1, self.party)

    def render(self):
        surface = super().render()
        surface.blit(self.map_bg, (0, 0))
        surface.blit(self.title_surface, (80, 148))
        surface.blit(self.party.leader.render(), (100, 100))
        surface.set_alpha(self.alpha)
        return surface

    def get_title_surface(self) -> pygame.Surface:
        title = text.TextBuilder.build_color(text.BROWN, self.dungeon_data.name)
        surface = Frame((21, 4))
        rect = title.get_rect(center=surface.get_rect().center)
        surface.blit(title, rect.topleft)
        return surface
