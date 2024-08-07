import pygame
import pygame.image
from app.common.action import Action
from app.common.inputstream import InputStream
from app.common import constants, menu, settings
from app.ground.movement_system import MovementSystem
from app.ground import ground, ground_data, ground_menu
from app.pokemon.party import Party
from app.pokemon import pokemon
from app.scenes.scene import Scene
from app.scenes.start_dungeon_scene import StartDungeonScene


class StartGroundScene(Scene):
    def __init__(self, scene_id, party: Party, location: int = 0):
        super().__init__(1, 1)
        ground_scene_data = ground_data.GroundSceneData(scene_id, location)
        g = ground.Ground(ground_scene_data, party)
        self.next_scene = GroundScene(g)


class GroundScene(Scene):
    def __init__(self, ground: ground.Ground):
        super().__init__(30, 30)
        self.ground = ground
        self.movement_system = MovementSystem(ground)
        self.party = self.ground.party
        self.set_camera_target(self.party.leader)
        self.menu: menu.Menu = None

        self.destination_menu = ground_menu.DestinationMenu()

    def set_camera_target(self, target: pokemon.Pokemon):
        self.camera_target = target
        self.camera = pygame.Rect((0, 0), constants.DISPLAY_SIZE)
        self.camera.centerx = target.x
        self.camera.centery = target.y
        if self.camera.left < 0:
            self.camera.left = 0
        elif self.camera.right > self.ground.width:
            self.camera.right = self.ground.width
        if self.camera.top < 0:
            self.camera.top = 0
        elif self.camera.bottom > self.ground.height:
            self.camera.bottom = self.ground.height

    def process_input(self, input_stream: InputStream):
        super().process_input(input_stream)
        kb = input_stream.keyboard
        if kb.is_pressed(pygame.K_r):
            self.ground.reload()
        if kb.is_pressed(pygame.K_t):
            self.ground.toggle_render_mode()
        if self.in_transition:
            return
        if self.menu is not None:
            self.menu.process_input(input_stream)
            if kb.is_pressed(settings.get_key(Action.MENU)):
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
            if (
                isinstance(self.menu, ground_menu.DestinationMenu)
                and self.menu.dungeon_id is not None
            ):
                self.next_scene = StartDungeonScene(self.menu.dungeon_id, self.party)
        else:
            self.movement_system.update()
            self.set_camera_target(self.party.leader)
            self.ground.update()
            self.next_ground()
            if self.ground.menu is None:
                self.destination_menu.cancelled = False
            else:
                if (
                    self.ground.menu == "destination_menu"
                    and not self.destination_menu.cancelled
                ):
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
            trigger = self.ground.trigger
            sx1 = int(trigger.data["sx1"]) * 8
            sy1 = int(trigger.data["sy1"]) * 8
            sx2 = int(trigger.data["sx2"]) * 8
            sy2 = int(trigger.data["sy2"]) * 8
            f = int(trigger.data["f"])
            self.party.leader.spawn((sx1, sy1))
            self.party[1].spawn((sx2, sy2))
            for p in self.party:
                for _ in range(f):
                    p.direction = p.direction.clockwise()
            self.next_scene = StartGroundScene(
                self.ground.ground_scene_data.scene_id, self.party, next_ground
            )
