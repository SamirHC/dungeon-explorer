import pygame
import pygame.image
from dungeon_explorer.common import direction, inputstream, constants, menu
from dungeon_explorer.ground import ground, grounddata, movementsystem, groundmenu
from dungeon_explorer.pokemon import party, pokemon
from dungeon_explorer.scenes import scene
from dungeon_explorer.scenes.dungeon import StartDungeonScene


class StartGroundScene(scene.Scene):
    def __init__(self, scene_id, party: party.Party, location: int=0):
        super().__init__(1, 1)
        ground_scene_data = grounddata.GroundSceneData(scene_id, location)
        g = ground.Ground(ground_scene_data, party)
        self.next_scene = GroundScene(g)


class GroundScene(scene.Scene):
    def __init__(self, ground: ground.Ground):
        super().__init__(30, 30)
        self.ground = ground
        self.movement_system = movementsystem.MovementSystem(ground)
        self.party = self.ground.party
        self.set_camera_target(self.party.leader)
        self.menu: menu.Menu = None

        self.destination_menu = groundmenu.DestinationMenu()

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
        super().process_input(input_stream)
        if self.in_transition:
            return
        if self.menu is not None:
            self.menu.process_input(input_stream)
            if input_stream.keyboard.is_pressed(pygame.K_n):
                if self.menu is self.destination_menu:
                    self.destination_menu.cancelled = True
                    self.menu = None
            return
        self.movement_system.process_input(input_stream)

    def update(self):
        super().update()
        if self.in_transition:
            return
        for p in self.ground.spawned:
            p.update()
        if self.menu is not None:
            self.menu.update()
            if isinstance(self.menu, groundmenu.DestinationMenu) and self.menu.dungeon_id is not None:
                self.next_scene = StartDungeonScene(self.menu.dungeon_id, self.party)
        else:
            self.movement_system.update()
            self.set_camera_target(self.party.leader)
            self.ground.update()
            self.next_ground()
            if self.ground.menu is None:
                self.destination_menu.cancelled = False
            else:
                if self.ground.menu == "destination_menu" and not self.destination_menu.cancelled:
                    self.menu = self.destination_menu

    def render(self) -> pygame.Surface:
        surface = super().render()
        floor_surface = self.ground.render()
        surface.blit(floor_surface, (0, 0), self.camera)
        if self.menu is not None:
            surface.blit(self.menu.render(), (0, 0))
        surface.set_alpha(self.alpha)
        return surface

    def next_ground(self):
        next_ground = self.ground.next_ground
        if next_ground is not None:
            new_party = party.Party([pokemon.UserPokemon(p.user_id) for p in self.party])
            self.next_scene = StartGroundScene(self.ground.ground_scene_data.scene_id, new_party, next_ground)
