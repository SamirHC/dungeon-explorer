import pygame
from dungeon_explorer.common import direction, inputstream, constants
from dungeon_explorer.ground import ground
from dungeon_explorer.pokemon import party, pokemon
from dungeon_explorer.scenes import scene


class GroundScene(scene.Scene):
    def __init__(self, ground: ground.Ground, party: party.Party):
        super().__init__()
        self.ground = ground
        self.party = party
        for p in self.party:
            p.spawn(ground.ground_data.spawn)
        self.set_camera_target(party.leader)

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
        kb = input_stream.keyboard
        if kb.is_pressed(pygame.K_w) or kb.is_held(pygame.K_w):
            self.party.leader.direction = direction.Direction.NORTH
            self.party.leader.move()
        elif kb.is_pressed(pygame.K_a) or kb.is_held(pygame.K_a):
            self.party.leader.direction = direction.Direction.WEST
            self.party.leader.move()
        elif kb.is_pressed(pygame.K_s) or kb.is_held(pygame.K_s):
            self.party.leader.direction = direction.Direction.SOUTH
            self.party.leader.move()
        elif kb.is_pressed(pygame.K_d) or kb.is_held(pygame.K_d):
            self.party.leader.direction = direction.Direction.EAST
            self.party.leader.move()

    def update(self):
        for p in self.party:
            p.update()
        self.set_camera_target(self.party.leader)

    def render(self) -> pygame.Surface:
        surface = super().render()
        floor_surface = self.ground.render()
        for p in self.party:
            sprite_surface = p.render()
            sprite_rect = sprite_surface.get_rect(center=p.position)
            if sprite_rect.colliderect(self.camera):
                floor_surface.blit(sprite_surface, sprite_rect)
        surface.blit(floor_surface, (0, 0), self.camera)
        return surface