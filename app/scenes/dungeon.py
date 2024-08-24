import pygame

from enum import Enum, auto
from collections import deque
from app.common.action import Action
from app.common.inputstream import InputStream
from app.common import constants, mixer, settings
from app.dungeon.battle_system import BattleSystem
from app.dungeon.movement_system import MovementSystem
from app.dungeon.dungeon import Dungeon
from app.dungeon.dungeon_data import DungeonData
from app.dungeon.menu.dungeon_menu import DungeonMenu
from app.dungeon.dungeon_map import DungeonMap
from app.dungeon.minimap import Minimap
from app.dungeon.hud import Hud
from app.dungeon.weather import Weather
from app.gui.textbox import DungeonTextBox, DungeonMessageLog
from app.events.event import Event
from app.events import game_event
from app.events.dungeon_event_handler import DungeonEventHandler
from app.events import start_turn_event
from app.pokemon.party import Party
from app.pokemon.pokemon import Pokemon
from app.pokemon.animation_id import AnimationId
from app.pokemon.status_effect import StatusEffect
from app.scenes.scene import Scene
from app.scenes import mainmenu
import app.db.database as db
from app.gui import shadow, text


class FloorTransitionScene(Scene):
    def __init__(self, dungeon_data: DungeonData, floor_num: int, party: Party):
        super().__init__(60, 60)
        self.dungeon_data = dungeon_data
        self.floor_num = floor_num
        self.party = party
        self.dungeon_name_banner = (
            text.TextBuilder()
            .set_font(db.font_db.banner_font)
            .set_alignment(text.Align.CENTER)
            .write(dungeon_data.banner)
            .build()
            .render()
        )
        self.floor_num_banner = (
            text.TextBuilder()
            .set_font(db.font_db.banner_font)
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
        return surface


TILE_SIZE = 24


class GameState(Enum):
    MENU = auto()
    PLAYING = auto()
    PROCESSING = auto()


class DungeonScene(Scene):
    def __init__(self, dungeon: Dungeon):
        super().__init__(30, 30)
        self.user = dungeon.user
        self.dungeon = dungeon
        self.dungeonmap = DungeonMap(self.dungeon)
        self.minimap = Minimap(self.dungeon.floor, self.dungeon.tileset.minimap_color)
        self.hud = Hud(self.user, self.dungeon)
        self.dungeon_log = DungeonTextBox()
        self.message_log = DungeonMessageLog(self.dungeon_log)

        self.event_queue: deque[Event] = deque()
        self.battle_system = BattleSystem(self.dungeon)
        self.movement_system = MovementSystem(self.dungeon)
        self.event_handler = DungeonEventHandler(
            dungeon, self.dungeon_log, self.event_queue, self.battle_system
        )

        self.set_camera_target(self.user)

        # Main Dungeon Menu
        self.menu = DungeonMenu(self.dungeon, self.battle_system)

        self.game_state = GameState.PLAYING

    def set_camera_target(self, target: Pokemon):
        self.camera_target = target
        e = target.moving_entity
        self.camera = pygame.Rect((0, 0), constants.DISPLAY_SIZE)
        self.camera.centerx = e.x + 12
        self.camera.centery = e.y + 4

    def process_debug_input(self, input_stream: InputStream):
        kb = input_stream.keyboard
        if kb.is_pressed(pygame.K_RIGHT):
            if self.dungeon.has_next_floor():
                self.next_scene = FloorTransitionScene(
                    self.dungeon.dungeon_data,
                    self.dungeon.floor_number + 1,
                    self.dungeon.party,
                )
            else:
                self.next_scene = mainmenu.MainMenuScene()
            return
        elif kb.is_down(pygame.K_EQUALS):
            self.dungeon.set_weather(Weather.CLOUDY)
        elif kb.is_down(pygame.K_MINUS):
            self.dungeon.set_weather(Weather.FOG)
        elif kb.is_down(pygame.K_0):
            self.dungeon.set_weather(Weather.CLEAR)
        elif kb.is_down(pygame.K_9):
            self.dungeon.set_weather(Weather.SUNNY)
        elif kb.is_down(pygame.K_8):
            self.dungeon.set_weather(Weather.SANDSTORM)
        elif kb.is_down(pygame.K_7):
            self.dungeon.set_weather(Weather.RAINY)
        elif kb.is_down(pygame.K_6):
            self.dungeon.set_weather(Weather.SNOW)
        elif kb.is_down(pygame.K_5):
            self.dungeon.set_weather(Weather.HAIL)

    def process_input(self, input_stream: InputStream):
        self.process_debug_input(input_stream)  # DEBUG
        if self.in_transition:
            return
        if self.game_state is GameState.PROCESSING:
            return
        if self.game_state is GameState.MENU:
            self.menu.process_input(input_stream)
            if self.menu.current_menu is None:
                self.game_state = GameState.PLAYING
        elif self.game_state is GameState.PLAYING:
            kb = input_stream.keyboard
            if kb.is_pressed(settings.get_key(Action.MENU)):
                self.game_state = GameState.MENU
                self.menu.process_input(input_stream)
            elif any(
                kb.is_down(settings.get_key(a))
                for a in (
                    Action.MOVE_1,
                    Action.MOVE_2,
                    Action.MOVE_3,
                    Action.MOVE_4,
                    Action.INTERACT,
                )
            ):
                self.game_state = GameState.PROCESSING
                self.battle_system.process_input(input_stream)
            elif any(
                kb.is_down(settings.get_key(a))
                for a in (
                    Action.UP,
                    Action.DOWN,
                    Action.LEFT,
                    Action.RIGHT,
                    Action.PASS,
                    Action.RUN,
                )
            ):
                self.game_state = GameState.PROCESSING
                self.movement_system.process_input(input_stream)

    def update_menu(self):
        self.menu.update()
        if self.menu.stairs_menu.proceed:
            self.menu.stairs_menu.proceed = False
            if self.dungeon.has_next_floor():
                self.next_scene = FloorTransitionScene(
                    self.dungeon.dungeon_data,
                    self.dungeon.floor_number + 1,
                    self.dungeon.party,
                )
            else:
                self.next_scene = mainmenu.MainMenuScene()

    def start_turn(self, pokemon: Pokemon):
        self.event_queue.extend(start_turn_event.start_turn(self.dungeon, pokemon))

    def ai_take_turn(self):
        for p in (p for p in self.dungeon.floor.spawned if p.has_turn):
            if not p.has_started_turn:
                self.start_turn(p)
                if not p.has_turn or self.event_queue:
                    break
            p.has_turn = False
            if self.battle_system.ai_attack(p):
                return
            self.movement_system.ai_move(p)

    def update_processing(self):
        if self.user.has_turn and not self.event_queue:
            self.game_state = GameState.PLAYING
            return

        # Determine AI intentions
        if (
            not self.movement_system.moving
            and not self.event_queue
            and not self.battle_system.attacker
            and not self.battle_system.current_move
        ):
            self.ai_take_turn()

        # Movement animations take priority
        if self.movement_system.to_move:
            self.movement_system.start()

        if self.movement_system.moving:
            self.movement_system.update()
            self.set_camera_target(self.user)
            return

        # Events such as battling/item interactions
        if self.battle_system.attacker and self.battle_system.current_move:
            self.event_queue.append(
                game_event.BattleSystemEvent(
                    self.dungeon,
                    self.battle_system.attacker,
                    self.battle_system.current_move,
                )
            )
            self.battle_system.deactivate()

        if self.event_queue:
            self.event_handler.update()
            
        # End scene if player loses.
        if not self.event_queue and self.dungeon.user_is_dead():
            # TODO: Display statistics and play lose scene.
            self.next_scene = mainmenu.MainMenuScene()
            return


        # Next turn
        if (
            not self.movement_system.to_move
            and not self.event_queue
            and self.dungeon.is_next_turn()
        ):
            self.dungeon.next_turn()
            self.start_turn(self.user)

    def update(self):
        super().update()
        if self.in_transition:
            return
        for p in self.dungeon.floor.spawned:
            p.update()
        self.dungeon_log.update()
        self.dungeon.tileset.update()
        self.minimap.update()
        self.set_camera_target(self.user)

        if self.game_state is GameState.MENU:
            self.update_menu()
        elif self.game_state is GameState.PROCESSING:
            self.update_processing()

    def render(self) -> pygame.Surface:
        surface = super().render()

        TILE_SIZE = self.dungeon.tileset.tile_size
        tile_rect = pygame.Rect(0, 0, TILE_SIZE, TILE_SIZE)

        floor_surface = self.dungeonmap.render(self.camera)

        # Draws sprites row by row of dungeon map
        for pokemon in sorted(self.dungeon.floor.spawned, key=lambda s: s.y):
            tile_rect.x = pokemon.moving_entity.x
            tile_rect.y = pokemon.moving_entity.y

            sprite_surface = pokemon.render()
            sprite_rect = sprite_surface.get_rect(center=tile_rect.center)

            shadow_surface = shadow.get_dungeon_shadow(
                pokemon.sprite.shadow_size, pokemon.is_enemy
            )
            shadow_rect = shadow_surface.get_rect(
                center=pygame.Vector2(sprite_rect.topleft)
                + pygame.Vector2(pokemon.sprite.current_shadow_position)
            )

            if sprite_rect.colliderect(self.camera):
                floor_surface.blit(shadow_surface, shadow_rect)
                if not (
                    pokemon.status.has_status_effect(StatusEffect.DIGGING)
                    and pokemon.animation_id is AnimationId.IDLE
                ):
                    floor_surface.blit(sprite_surface, sprite_rect)

            if self.event_queue:
                ev = self.event_queue[0]
                if (
                    isinstance(ev, game_event.StatAnimationEvent)
                    and ev.target is pokemon
                ):
                    move_surface = ev.anim.get_current_frame()
                    move_rect = move_surface.get_rect(
                        bottom=tile_rect.bottom, centerx=tile_rect.centerx
                    )
                    if move_rect.colliderect(self.camera):
                        floor_surface.blit(move_surface, move_rect)

        floor_surface = floor_surface.subsurface(self.camera)

        surface.blit(floor_surface, (0, 0))
        surface.blit(self.hud.render(), (0, 0))

        if self.game_state is GameState.MENU:
            surface.blit(self.menu.render(), (0, 0))
        else:
            surface.blit(self.minimap.render(), (0, 0))
            surface.blit(self.dungeon_log.render(), (8, 128))

        return surface
