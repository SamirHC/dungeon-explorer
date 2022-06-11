import pygame
import pygame.display
import pygame.image
import pygame.mixer
from dungeon_explorer.common import constants, inputstream, text, mixer
from dungeon_explorer.dungeon import battlesystem, dungeon, dungeonmap, dungeondata, dungeonmenu, dungeonstatus, minimap, hud, movementsystem
from dungeon_explorer.pokemon import party, pokemon
from dungeon_explorer.scenes import scene, mainmenu


class StartDungeonScene(scene.Scene):
    def __init__(self, dungeon_id: int, party: party.Party):
        super().__init__(30, 30)
        dungeon_data = dungeondata.DungeonData(dungeon_id)
        self.next_scene = FloorTransitionScene(dungeon_data, 1, party)


class FloorTransitionScene(scene.Scene):
    def __init__(self, dungeon_data: dungeondata.DungeonData, floor_num: int, party: party.Party):
        super().__init__(60, 60)
        self.dungeon_data = dungeon_data
        self.floor_num = floor_num
        self.party = party
        self.dungeon_name_banner = (
            text.TextBuilder()
            .set_font(text.banner_font)
            .set_alignment(text.Align.CENTER)
            .write(dungeon_data.banner)
            .build()
            .render()
        )
        self.floor_num_banner = (
            text.TextBuilder()
            .set_font(text.banner_font)
            .write(self.floor_string)
            .build()
            .render()
        )

    @property
    def floor_string(self) -> str:
        result = "B" if self.dungeon_data.is_below else ""
        result += str(self.floor_num) + "F"
        return result

    def update(self):
        super().update()
        if self.in_transition:
            return
        for p in self.party:
            p.status.restore_stats()
            p.status.restore_status()
        self.dungeon = dungeon.Dungeon(self.dungeon_data, self.floor_num, self.party)
        mixer.set_bgm(self.dungeon.current_floor_data.bgm)
        self.next_scene = DungeonScene(self.dungeon)
    
    def render(self):
        surface = super().render()
        cx = surface.get_rect().centerx
        rect = self.dungeon_name_banner.get_rect(center=(cx, 72))
        surface.blit(self.dungeon_name_banner, rect.topleft)
        rect = self.floor_num_banner.get_rect(center=(cx, rect.bottom + 24))
        surface.blit(self.floor_num_banner, rect.topleft)
        surface.set_alpha(self.alpha)
        return surface


class DungeonScene(scene.Scene):
    def __init__(self, dungeon: dungeon.Dungeon):
        super().__init__(30, 30)
        self.user = dungeon.user
        self.dungeon = dungeon
        self.dungeonmap = dungeonmap.DungeonMap(self.dungeon)
        self.minimap = minimap.MiniMap(self.dungeon)
        self.battle_system = battlesystem.BattleSystem(self.dungeon)
        self.movement_system = movementsystem.MovementSystem(self.dungeon)
        self.hud = hud.Hud(self.user, self.dungeon)
        self.set_camera_target(self.user)
        
        # Main Dungeon Menu
        self.menu = dungeonmenu.DungeonMenu(self.dungeon, self.battle_system)

    def set_camera_target(self, target: pokemon.Pokemon):
        self.camera_target = target
        self.camera = pygame.Rect((0, 0), constants.DISPLAY_SIZE)
        self.camera.centerx = (target.x + 5) * self.dungeon.tileset.tile_size + 12
        self.camera.centery = (target.y + 5) * self.dungeon.tileset.tile_size + 4

    @property
    def is_system_active(self) -> bool:
        return self.movement_system.is_active or self.battle_system.is_active

    @property
    def is_system_waiting(self) -> bool:
        return self.movement_system.is_waiting or self.battle_system.is_waiting

    def in_menu(self):
        return self.menu.is_active

    def process_input(self, input_stream: inputstream.InputStream):
        if self.in_transition:
            return
        if not self.user.has_turn:
            return
        # DEBUG PURPOSES
        if input_stream.keyboard.is_pressed(pygame.K_RIGHT):
            if self.dungeon.has_next_floor():
                self.next_scene = FloorTransitionScene(self.dungeon.dungeon_data, self.dungeon.floor_number+1, self.dungeon.party)
            else:
                self.next_scene = mainmenu.MainMenuScene()
            return
        elif input_stream.keyboard.is_pressed(pygame.K_EQUALS):
            self.dungeon.weather = dungeonstatus.Weather.CLOUDY
        elif input_stream.keyboard.is_pressed(pygame.K_MINUS):
            self.dungeon.weather = dungeonstatus.Weather.FOG
        elif input_stream.keyboard.is_pressed(pygame.K_0):
            self.dungeon.weather = dungeonstatus.Weather.CLEAR
        elif input_stream.keyboard.is_pressed(pygame.K_9):
            self.dungeon.weather = dungeonstatus.Weather.SUNNY
        elif input_stream.keyboard.is_pressed(pygame.K_8):
            self.dungeon.weather = dungeonstatus.Weather.SANDSTORM
        elif input_stream.keyboard.is_pressed(pygame.K_7):
            self.dungeon.weather = dungeonstatus.Weather.RAINY
        elif input_stream.keyboard.is_pressed(pygame.K_6):
            self.dungeon.weather = dungeonstatus.Weather.SNOW
        elif input_stream.keyboard.is_pressed(pygame.K_5):
            self.dungeon.weather = dungeonstatus.Weather.HAIL
        #
        if not self.in_menu():
            if self.battle_system.process_input(input_stream):
                return
            self.movement_system.input(input_stream)
        self.menu.process_input(input_stream)

    def update(self):
        super().update()
        for sprite in self.dungeon.spawned:
            sprite.update()
            
        self.dungeon.dungeon_log.update()
        self.dungeon.tileset.update()
        self.minimap.update()
    
        if self.in_menu():
            self.menu.update()
            if self.menu.stairs_menu.proceed:
                self.menu.stairs_menu.proceed = False
                if self.dungeon.has_next_floor():
                    self.next_scene = FloorTransitionScene(self.dungeon.dungeon_data, self.dungeon.floor_number+1, self.dungeon.party)
                else:
                    self.next_scene = mainmenu.MainMenuScene()
                return
        
        if not self.user.has_turn and not self.is_system_active and not self.battle_system.is_waiting:
            for sprite in self.dungeon.spawned:
                if not sprite.has_turn:
                    continue
                sprite.has_turn = False
                if self.battle_system.ai_attack(sprite):
                    break
                else:
                    self.movement_system.ai_move(sprite)
    
        if not self.is_system_active:
            if self.movement_system.is_waiting:
                self.movement_system.start()
            elif self.battle_system.is_waiting:
                self.battle_system.is_active = True

        self.movement_system.update()
        self.battle_system.update()

        if not self.is_system_active:
            if self.dungeon.user_is_dead():
                self.next_scene = mainmenu.MainMenuScene()
            elif self.dungeon.user_at_stairs() and not self.menu.stairs_menu.cancelled and self.user.has_turn:
                self.menu.current_menu = self.menu.stairs_menu
                self.menu.stairs_menu.auto = True

            if not self.dungeon.user_at_stairs() and self.menu.stairs_menu.cancelled:
                self.menu.stairs_menu.cancelled = False

            if not self.is_system_waiting:
                if self.dungeon.is_next_turn():
                    self.dungeon.next_turn()

    def render(self) -> pygame.Surface:
        surface = super().render()
        TILE_SIZE = self.dungeon.tileset.tile_size

        if self.camera_target in self.movement_system.moving:
            self.camera.centerx = (self.camera_target.x + 5) * self.dungeon.tileset.tile_size + 12
            self.camera.centery = (self.camera_target.y + 5) * self.dungeon.tileset.tile_size + 4
            self.camera.center -= pygame.Vector2(self.camera_target.direction.value) * int(self.movement_system.movement_fraction * TILE_SIZE)
        
        floor_surface = pygame.Surface(pygame.Vector2(self.dungeon.floor.WIDTH + 10, self.dungeon.floor.HEIGHT + 10)*TILE_SIZE)
        tile_rect = pygame.Rect(0, 0, TILE_SIZE, TILE_SIZE)
        for xi, x in enumerate(range(-5, self.dungeon.floor.WIDTH + 5)):
            for yi, y in enumerate(range(-5, self.dungeon.floor.HEIGHT + 5)):
                tile_rect.topleft = xi*TILE_SIZE, yi*TILE_SIZE
                if tile_rect.colliderect(self.camera):
                    tile_surface = self.dungeonmap[x, y]
                    floor_surface.blit(tile_surface, tile_rect)
        
        # Draws sprites row by row of dungeon map
        for sprite in sorted(self.dungeon.spawned, key=lambda s: s.y):
            tile_rect.x = TILE_SIZE * (sprite.x + 5)
            tile_rect.y = TILE_SIZE * (sprite.y + 5)
            if sprite in self.movement_system.moving:
                tile_rect.topleft -= pygame.Vector2(sprite.direction.value) * int(self.movement_system.movement_fraction * TILE_SIZE)
            sprite_surface = sprite.render()
            sprite_rect = sprite_surface.get_rect(center=tile_rect.center)
            if sprite_rect.colliderect(self.camera):
                floor_surface.blit(sprite_surface, sprite_rect)
            if self.battle_system.is_move_animation_event(sprite):
                move_surface = self.battle_system.render()
                move_rect = move_surface.get_rect(bottom=tile_rect.bottom, centerx=tile_rect.centerx)
                if move_rect.colliderect(self.camera):
                    floor_surface.blit(move_surface, move_rect)

        surface.blit(floor_surface, (0, 0), self.camera)
        
        surface.blit(self.hud.render(), (0, 0))

        if self.in_menu():
            surface.blit(self.menu.render(), (0, 0))
        else:
            surface.blit(self.minimap.render(), (0, 0))
            surface.blit(self.dungeon.dungeon_log.render(), (8, 128))

        surface.set_alpha(self.alpha)
        return surface
