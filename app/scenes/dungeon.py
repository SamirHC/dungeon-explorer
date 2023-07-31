import pygame
import pygame.display
import pygame.image
import pygame.mixer
import random
from collections import deque
from app.common.inputstream import InputStream
from app.common import constants, text, mixer
from app.dungeon.battlesystem import BattleSystem
from app.dungeon.movementsystem import MovementSystem
from app.dungeon.dungeon import Dungeon
from app.dungeon.dungeondata import DungeonData
from app.dungeon.dungeonmenu import DungeonMenu
from app.dungeon.dungeonmap import DungeonMap
from app.dungeon.minimap import MiniMap
from app.dungeon.hud import Hud
from app.dungeon.floorstatus import Weather
from app.events.event import Event, SleepEvent
from app.events import gameevent
from app.events.dungeoneventhandler import DungeonEventHandler
from app.pokemon.party import Party
from app.pokemon import pokemon
from app.scenes.scene import Scene
from app.scenes import mainmenu
from app.db import font_db


class StartDungeonScene(Scene):
    def __init__(self, dungeon_id: int, party: Party):
        super().__init__(30, 30)
        dungeon_data = DungeonData(dungeon_id)
        self.next_scene = FloorTransitionScene(dungeon_data, 1, party)


class FloorTransitionScene(Scene):
    def __init__(self, dungeon_data: DungeonData, floor_num: int, party: Party):
        super().__init__(60, 60)
        self.dungeon_data = dungeon_data
        self.floor_num = floor_num
        self.party = party
        self.dungeon_name_banner = (
            text.TextBuilder()
            .set_font(font_db.banner_font)
            .set_alignment(text.Align.CENTER)
            .write(dungeon_data.banner)
            .build()
            .render()
        )
        self.floor_num_banner = (
            text.TextBuilder()
            .set_font(font_db.banner_font)
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
        self.dungeon = Dungeon(self.dungeon_data, self.floor_num, self.party)
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


class DungeonScene(Scene):
    def __init__(self, dungeon: Dungeon):
        super().__init__(30, 30)
        self.user = dungeon.user
        self.dungeon = dungeon
        self.dungeonmap = DungeonMap(self.dungeon)
        self.minimap = MiniMap(self.dungeon.floor, self.dungeon.tileset.minimap_color)
        self.hud = Hud(self.user, self.dungeon)

        self.event_queue: deque[Event] = deque()
        self.event_handler = DungeonEventHandler(dungeon, self.event_queue)
        self.battle_system = BattleSystem(self.dungeon, self.event_queue)
        self.movement_system = MovementSystem(self.dungeon)
        
        self.set_camera_target(self.user)
        
        # Main Dungeon Menu
        self.menu = DungeonMenu(self.dungeon, self.battle_system)

    def set_camera_target(self, target: pokemon.Pokemon):
        self.camera_target = target
        self.camera = pygame.Rect((0, 0), constants.DISPLAY_SIZE)
        self.camera.centerx = (target.x + 5) * self.dungeon.tileset.tile_size + 12
        self.camera.centery = (target.y + 5) * self.dungeon.tileset.tile_size + 4

    def in_menu(self):
        return self.menu.is_active
    
    def process_debug_input(self, input_stream: InputStream):
        if input_stream.keyboard.is_pressed(pygame.K_RIGHT):
            if self.dungeon.has_next_floor():
                self.next_scene = FloorTransitionScene(self.dungeon.dungeon_data, self.dungeon.floor_number+1, self.dungeon.party)
            else:
                self.next_scene = mainmenu.MainMenuScene()
            return
        elif input_stream.keyboard.is_pressed(pygame.K_EQUALS):
            self.dungeon.set_weather(Weather.CLOUDY)
        elif input_stream.keyboard.is_pressed(pygame.K_MINUS):
            self.dungeon.set_weather(Weather.FOG)
        elif input_stream.keyboard.is_pressed(pygame.K_0):
            self.dungeon.set_weather(Weather.CLEAR)
        elif input_stream.keyboard.is_pressed(pygame.K_9):
            self.dungeon.set_weather(Weather.SUNNY)
        elif input_stream.keyboard.is_pressed(pygame.K_8):
            self.dungeon.set_weather(Weather.SANDSTORM)
        elif input_stream.keyboard.is_pressed(pygame.K_7):
            self.dungeon.set_weather(Weather.RAINY)
        elif input_stream.keyboard.is_pressed(pygame.K_6):
            self.dungeon.set_weather(Weather.SNOW)
        elif input_stream.keyboard.is_pressed(pygame.K_5):
            self.dungeon.set_weather(Weather.HAIL)

    def check_sprite_asleep(self, sprite: pokemon.Pokemon):
        if sprite.status.asleep:
            sprite.status.asleep -= 1
            if sprite.status.asleep == 0:
                text_surface = (
                    text.TextBuilder()
                    .set_shadow(True)
                    .set_color(sprite.name_color)
                    .write(sprite.name)
                    .set_color(text.WHITE)
                    .write(" woke up!")
                    .build()
                    .render()
                )
                self.event_queue.append(gameevent.LogEvent(text_surface).with_divider())
                self.event_queue.append(gameevent.SetAnimationEvent(sprite, sprite.sprite.IDLE_ANIMATION_ID, True))
                self.event_queue.append(SleepEvent(20))
            else:
                sprite.has_turn = False
                # Only to alert user why they cannot make a move.
                if sprite is self.user:
                    text_surface = (
                        text.TextBuilder()
                        .set_shadow(True)
                        .set_color(sprite.name_color)
                        .write(sprite.name)
                        .set_color(text.WHITE)
                        .write(" is asleep!")
                        .build()
                        .render()
                    )
                    self.event_queue.append(gameevent.LogEvent(text_surface))
                    self.event_queue.append(SleepEvent(20))
        if sprite.status.yawning:
            sprite.status.yawning -= 1
            if sprite.status.yawning == 0:
                sprite.has_turn = False
                self.battle_system.defender = sprite
                self.event_queue.extend(self.battle_system.get_asleep_events())
        
        if sprite.status.nightmare:
            sprite.status.nightmare -= 1
            if sprite.status.nightmare == 0:
                self.battle_system.defender = sprite
                self.event_queue.extend(self.battle_system.get_nightmare_events())
            else:
                sprite.has_turn = False
                if sprite is self.user:
                    text_surface = (
                        text.TextBuilder()
                        .set_shadow(True)
                        .set_color(sprite.name_color)
                        .write(sprite.name)
                        .set_color(text.WHITE)
                        .write(" is asleep!")
                        .build()
                        .render()
                    )
                    self.event_queue.append(gameevent.LogEvent(text_surface))
                    self.event_queue.append(SleepEvent(20))

    def process_input(self, input_stream: InputStream):
        if self.in_transition:
            return
        self.check_sprite_asleep(self.user)
        if not self.user.has_turn:
            return
        
        self.process_debug_input(input_stream)  # DEBUG
        
        if not self.in_menu() and not self.event_queue:
            if self.battle_system.process_input(input_stream):
                return
            self.movement_system.process_input(input_stream)
        self.menu.process_input(input_stream)

    def update(self):
        super().update()
        for sprite in self.dungeon.floor.spawned:
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
        
        if not self.user.has_turn and not self.movement_system.is_active and not self.event_queue:
            for sprite in self.dungeon.floor.spawned:
                if not sprite.has_turn:
                    continue
                self.check_sprite_asleep(sprite)
                if sprite.hp_status <= 0:
                    break
                if not sprite.has_turn:
                    continue
                sprite.has_turn = False
                if self.battle_system.ai_attack(sprite):
                    break
                else:
                    self.movement_system.ai_move(sprite)
    
        if self.movement_system.is_waiting:
            self.movement_system.start()

        self.movement_system.update()
        if (not self.movement_system.is_active):
            self.event_handler.update()

        if not self.movement_system.is_active:
            if self.dungeon.user_is_dead():
                self.next_scene = mainmenu.MainMenuScene()
            elif self.dungeon.floor.user_at_stairs() and not self.menu.stairs_menu.cancelled and self.user.has_turn:
                self.menu.current_menu = self.menu.stairs_menu
                self.menu.stairs_menu.auto = True

            if not self.dungeon.floor.user_at_stairs() and self.menu.stairs_menu.cancelled:
                self.menu.stairs_menu.cancelled = False

            if not self.movement_system.is_waiting:
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
                    item = self.dungeon.floor[x, y].item_ptr
                    if item is not None:
                        floor_surface.blit(item.surface, tile_rect.move(4, 4))
        
        # Draws sprites row by row of dungeon map
        for sprite in sorted(self.dungeon.floor.spawned, key=lambda s: s.y):
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
