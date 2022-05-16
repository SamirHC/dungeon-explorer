import pygame
import pygame.display
import pygame.image
import pygame.mixer
from dungeon_explorer.common import constants, inputstream, text, mixer
from dungeon_explorer.dungeon import battlesystem, dungeon, dungeonmap, dungeondata, dungeonmenu, dungeonstatus, minimap, hud, movementsystem
from dungeon_explorer.pokemon import party
from dungeon_explorer.scenes import scene, mainmenu


class StartDungeonScene(scene.Scene):
    def __init__(self, dungeon_id: str, party: party.Party):
        super().__init__()
        dungeon_data = dungeondata.DungeonData(dungeon_id)
        self.next_scene = FloorTransitionScene(dungeon_data, 1, party)


class FloorTransitionScene(scene.TransitionScene):
    def __init__(self, dungeon_data: dungeondata.DungeonData, floor_num: int, party: party.Party):
        super().__init__(200)

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

        self.alpha = 0
        self.fade_in = 30
        self.fade_out = 170
        self.text_fade_in = 60
        self.text_fade_out = 140
        self.text_alpha = 0

    @property
    def floor_string(self) -> str:
        result = "B" if self.dungeon_data.is_below else ""
        result += str(self.floor_num) + "F"
        return result

    def update(self):
        super().update()
        if self.timer < self.fade_in:
            self.alpha = (255 * self.timer) // 30
        elif self.timer > self.fade_out:
            self.alpha = (255 * (self.end_time - self.timer)) // 30
        else:
            self.alpha = 255

        if self.timer == 100:
            self.dungeon = dungeon.Dungeon(self.dungeon_data, self.floor_num, self.party)
            mixer.set_bgm(self.dungeon.current_floor_data.bgm)

        if self.timer < self.text_fade_in:
            self.text_alpha = (255 * (self.timer - self.fade_in)) // 30
        elif self.timer > self.text_fade_out:
            self.text_alpha = (255 * (self.fade_out - self.timer)) // 30
        else:
            self.text_alpha = 255
    
    def render(self):
        surface = super().render()
        cx = surface.get_rect().centerx
        surface.set_alpha(self.alpha)
        self.dungeon_name_banner.set_alpha(self.text_alpha)
        self.floor_num_banner.set_alpha(self.text_alpha)
        rect = self.dungeon_name_banner.get_rect(center=(cx, 72))
        surface.blit(self.dungeon_name_banner, rect.topleft)
        rect = self.floor_num_banner.get_rect(center=(cx, rect.bottom + 24))
        surface.blit(self.floor_num_banner, rect.topleft)
        return surface

    def end_scene(self):
        self.next_scene = DungeonScene(self.dungeon)

class DungeonScene(scene.Scene):
    def __init__(self, dungeon: dungeon.Dungeon):
        super().__init__()
        self.user = dungeon.user
        self.dungeon = dungeon
        self.dungeonmap = dungeonmap.DungeonMap(self.dungeon)
        self.minimap = minimap.MiniMap(self.dungeon)
        self.battle_system = battlesystem.BattleSystem(self.dungeon)
        self.movement_system = movementsystem.MovementSystem(self.dungeon)
        self.hud = hud.Hud(self.user, self.dungeon)
        
        # Main Dungeon Menu
        self.menu = dungeonmenu.DungeonMenu(self.dungeon, self.battle_system)

    @property
    def is_system_active(self) -> bool:
        return self.movement_system.is_active or self.battle_system.is_active

    @property
    def is_system_waiting(self) -> bool:
        return self.movement_system.is_waiting or self.battle_system.is_waiting

    def in_menu(self):
        return self.menu.is_active

    def process_input(self, input_stream: inputstream.InputStream):
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
        surface = pygame.Surface(constants.DISPLAY_SIZE)
        display_rect = surface.get_rect()
        TILE_SIZE = self.dungeon.tileset.tile_size
        tile_rect = pygame.Rect(0, 0, TILE_SIZE, TILE_SIZE)
        if self.user in self.movement_system.moving:
            offset = pygame.Vector2(self.user.direction.value) * int(self.movement_system.movement_fraction * TILE_SIZE)
        else:
            offset = pygame.Vector2(0, 0)
        tile_rect.center = pygame.Vector2(surface.get_rect().center) + offset
        dx0 = (tile_rect.x - display_rect.x) // TILE_SIZE + 1
        dy0 = (tile_rect.y - display_rect.y) // TILE_SIZE + 1
        w = display_rect.width // TILE_SIZE + 1
        h = display_rect.height // TILE_SIZE + 1
        x0 = self.user.x - dx0
        y0 = self.user.y - dy0
        x1 = x0 + w
        y1 = y0 + h
        tile_rect.x -= dx0 * TILE_SIZE
        tile_rect.y -= dy0 * TILE_SIZE
        tile_rect_x0, tile_rect_y0 = tile_rect.topleft
        render_range_x = range(x0, x1 + 1)
        render_range_y = range(y0, y1 + 1)
        for xi, x in enumerate(render_range_x):
            for yi, y in enumerate(render_range_y):
                tile_surface = self.dungeonmap[x, y]
                tile_rect.x = tile_rect_x0 + TILE_SIZE * xi
                tile_rect.y = tile_rect_y0 + TILE_SIZE * yi
                surface.blit(tile_surface, tile_rect.topleft)

        # Draws sprites row by row of dungeon map
        for sprite in sorted(self.dungeon.spawned, key=lambda s: s.y):
            if sprite.x in render_range_x and sprite.y in render_range_y:
                if sprite in self.movement_system.moving:
                    offset = pygame.Vector2(sprite.direction.value) * int(self.movement_system.movement_fraction * TILE_SIZE)
                else:
                    offset = pygame.Vector2(0, 0)
                tile_rect.x = tile_rect_x0 + TILE_SIZE * (sprite.x - x0) - offset.x
                tile_rect.y = tile_rect_y0 + TILE_SIZE * (sprite.y - y0) - offset.y
                sprite_surface = sprite.render()
                sprite_rect = sprite_surface.get_rect(center=tile_rect.center)
                surface.blit(sprite_surface, sprite_rect)

        surface.blit(self.hud.render(), (0, 0))

        if self.in_menu():
            surface.blit(self.menu.render(), (0, 0))
            return surface

        surface.blit(self.minimap.render(), (0, 0))
        surface.blit(self.dungeon.dungeon_log.render(), (8, 128))

        return surface
