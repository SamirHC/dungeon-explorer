import os
import pygame
import pygame.image
from dungeon_explorer.common import direction, inputstream, constants
from dungeon_explorer.ground import ground, grounddata, movementsystem
from dungeon_explorer.pokemon import party, pokemon
from dungeon_explorer.scenes import scene


class StartGroundScene(scene.Scene):
    def __init__(self, scene_id, party: party.Party):
        ground_data = grounddata.get_ground_data(scene_id)
        g = ground.Ground(ground_data, party)
        self.next_scene = GroundScene(g)

class GroundScene(scene.Scene):
    def __init__(self, ground: ground.Ground):
        super().__init__()
        self.ground = ground
        self.movement_system = movementsystem.MovementSystem(ground)
        self.party = self.ground.party
        self.set_camera_target(self.party.leader)

    def set_camera_target(self, target: pokemon.Pokemon):
        self.camera_target = target
        self.camera = pygame.Rect((0, 0), constants.DISPLAY_SIZE)
        self.camera.centerx = target.x
        self.camera.centery = target.y
        if self.camera.left < 0:
            self.camera.left = 0
        elif self.camera.right > self.ground.ground_data.bg.get_width():
            self.camera.right = self.ground.ground_data.bg.get_width()
        if self.camera.top < 0:
            self.camera.top = 0
        elif self.camera.bottom > self.ground.ground_data.bg.get_height():
            self.camera.bottom = self.ground.ground_data.bg.get_height()
        
    def process_input(self, input_stream: inputstream.InputStream):
        self.movement_system.process_input(input_stream)

    def update(self):
        for p in self.ground.spawned:
            p.update()
        self.movement_system.update()
        self.set_camera_target(self.party.leader)

    def render(self) -> pygame.Surface:
        surface = super().render()
        floor_surface = self.ground.render()            
        surface.blit(floor_surface, (0, 0), self.camera)
        return surface