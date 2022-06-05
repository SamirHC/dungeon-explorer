import pygame
import pygame.image
from dungeon_explorer.common import direction, inputstream, constants
from dungeon_explorer.ground import ground, grounddata, movementsystem
from dungeon_explorer.pokemon import party, pokemon
from dungeon_explorer.scenes import scene


class StartGroundScene(scene.Scene):
    def __init__(self, scene_id, party: party.Party):
        ground_scene_data = grounddata.GroundSceneData(scene_id)
        g = ground.Ground(ground_scene_data, 0, party)
        self.next_scene = GroundScene(g)


class GroundTransitionScene(scene.TransitionScene):
    def __init__(self, ground_scene_data: grounddata.GroundSceneData, location_id: int, party: party.Party):
        super().__init__(20)
        self.ground_scene_data = ground_scene_data
        self.location_id = location_id
        self.party = party

        self.alpha = 0
        self.fade_in = 10
        self.fade_out = 10

    def update(self):
        super().update()
        if self.timer < self.fade_in:
            self.alpha = (255 * self.timer) // 30
        elif self.timer > self.fade_out:
            self.alpha = (255 * (self.end_time - self.timer)) // 30
        else:
            self.alpha = 255
        
        if self.timer == 10:
            self.ground = ground.Ground(self.ground_scene_data, self.location_id, self.party)
            #mixer.set_bgm(self.dungeon.current_floor_data.bgm)

    def render(self):
        surface = super().render()
        surface.set_alpha(self.alpha)
        return surface
    
    def end_scene(self):
        self.next_scene = GroundScene(self.ground)


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
        self.next_ground()

    def render(self) -> pygame.Surface:
        surface = super().render()
        floor_surface = self.ground.render()            
        surface.blit(floor_surface, (0, 0), self.camera)
        return surface

    def next_ground(self):
        next_ground = self.ground.next_ground(self.party.leader.position)
        if next_ground:
            self.next_scene = GroundTransitionScene(self.ground.ground_scene_data, next_ground, self.party)