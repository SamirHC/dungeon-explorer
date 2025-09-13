from enum import Enum, auto
from collections import deque
from functools import lru_cache

import pygame

from app.common.action import Action
from app.common.inputstream import InputStream
from app.common import constants, mixer, settings
from app.dungeon.battle_system import BattleSystem
from app.dungeon.movement_system import MovementSystem
from app.dungeon.dungeon import Dungeon
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
import app.db.dungeon_data as dungeon_data_db
import app.db.floor_data as floor_data_db
import app.db.database as main_db
import app.db.font as font_db
import app.db.colormap as colormap_db
import app.db.shadow as shadow_db
from app.gui import text
from app.dungeon.darkness_level import DarknessLevel
from app.item.inventory import Inventory


@lru_cache(maxsize=1)
def get_dungeon_name_banner(dungeon_id: int) -> pygame.Surface:
    return (
        text.TextBuilder()
        .set_font(font_db.banner_font)
        .set_alignment(text.Align.CENTER)
        .write(dungeon_data_db.load(dungeon_id).banner)
        .build()
        .render()
    )


@lru_cache(maxsize=1)
def get_floor_num_banner(dungeon_id: int, floor_num: int) -> pygame.Surface:
    return (
        text.TextBuilder()
        .set_font(font_db.banner_font)
        .write("B" if dungeon_data_db.load(dungeon_id).is_below else "")
        .write(f"{floor_num}F")
        .build()
        .render()
    )


class FloorTransitionScene(Scene):
    def __init__(
        self, dungeon_id: int, floor_num: int, party: Party, inventory: Inventory
    ):
        super().__init__(60, 60)
        self.dungeon_id = dungeon_id
        self.floor_num = floor_num
        self.party = party
        self.inventory = inventory

    def update(self):
        super().update()
        if self.in_transition:
            return
        for p in self.party:
            p.status.restore_stats()
            p.status.restore_status()

        mixer.set_bgm(floor_data_db.load(self.dungeon_id, self.floor_num).bgm)

        dungeon = Dungeon(self.dungeon_id, self.floor_num, self.party, self.inventory)
        self.next_scene = DungeonScene(dungeon)

    def render(self):
        surface = super().render()
        cx = surface.get_rect().centerx

        dungeon_name_banner = get_dungeon_name_banner(self.dungeon_id)
        rect = dungeon_name_banner.get_rect(center=(cx, 72))
        surface.blit(dungeon_name_banner, rect.topleft)

        floor_num_banner = get_floor_num_banner(self.dungeon_id, self.floor_num)
        rect = floor_num_banner.get_rect(center=(cx, rect.bottom + 24))
        surface.blit(floor_num_banner, rect.topleft)

        return surface


class GameState(Enum):
    MENU = auto()
    PLAYING = auto()
    PROCESSING = auto()


class DungeonScene(Scene):
    def __init__(self, dungeon: Dungeon):
        super().__init__(30, 30)
        self.dungeon = dungeon
        self.dungeonmap = DungeonMap(self.dungeon)
        self.minimap = Minimap(
            self.dungeon.floor, self.dungeon.floor.tileset.minimap_color
        )
        self.hud = Hud(dungeon)
        self.dungeon_log = DungeonTextBox()
        self.message_log = DungeonMessageLog()

        self.event_queue: deque[Event] = deque()
        self.battle_system = BattleSystem(self.dungeon)
        self.movement_system = MovementSystem(self.dungeon)
        self.event_handler = DungeonEventHandler(
            dungeon,
            self.dungeon_log,
            self.message_log,
            self.event_queue,
            self.battle_system,
        )

        self.set_camera_target(self.dungeon.party.leader)

        # Main Dungeon Menu
        self.menu = DungeonMenu(self.dungeon, self.battle_system, self.message_log)

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
            self.exit_floor()
            return
        elif kb.is_down(pygame.K_UP):
            self.next_scene = mainmenu.MainMenuScene()
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
            self.exit_floor()

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

    def exit_floor(self):
        if self.dungeon.has_next_floor:
            self.next_scene = FloorTransitionScene(
                self.dungeon.dungeon_id,
                self.dungeon.floor_number + 1,
                self.dungeon.party,
                self.dungeon.inventory,
            )
        else:
            self.next_scene = mainmenu.MainMenuScene()

    def update_processing(self):
        if self.dungeon.party.leader.has_turn and not self.event_queue:
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
            self.set_camera_target(self.dungeon.party.leader)
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
            self.start_turn(self.dungeon.party.leader)
            if self.dungeon.floor.user_at_stairs():
                self.menu.current_menu = self.menu.stairs_menu
                self.menu.stairs_menu.is_quick_access = True
                self.game_state = GameState.MENU

    def update(self):
        super().update()
        if self.in_transition:
            return
        for p in self.dungeon.floor.spawned:
            p.update()
        self.dungeon_log.update()
        self.dungeon.floor.tileset.update()
        self.minimap.update()
        self.set_camera_target(self.dungeon.party.leader)

        if self.game_state is GameState.MENU:
            self.update_menu()
        elif self.game_state is GameState.PROCESSING:
            self.update_processing()

    def render(self) -> pygame.Surface:
        surface = super().render()

        floor_surface = self.dungeonmap.render(self.camera)
        floor_surface = self.render_sprites(floor_surface)
        floor_surface = floor_surface.subsurface(self.camera)

        surface.blit(floor_surface, (0, 0))
        surface.blit(self.get_darkness_surface(), (0, 0))
        surface.blit(self.get_filter_surface(), (0, 0))

        surface.blit(self.hud.render(), (0, 0))

        if self.game_state is GameState.MENU:
            surface.blit(self.menu.render(), (0, 0))
        else:
            surface.blit(self.minimap.render(), (0, 0))
            surface.blit(self.dungeon_log.render(), (8, 128))

        return surface

    def render_sprites(self, floor_surface: pygame.Surface) -> pygame.Surface:
        TILE_SIZE = self.dungeon.floor.tileset.tile_size
        tile_rect = pygame.Rect(0, 0, TILE_SIZE, TILE_SIZE)

        for pokemon in sorted(self.dungeon.floor.spawned, key=lambda s: s.y):
            tile_rect.x = pokemon.moving_entity.x
            tile_rect.y = pokemon.moving_entity.y

            sprite_surface = pokemon.render()
            sprite_rect = sprite_surface.get_rect(center=tile_rect.center)

            if sprite_rect.colliderect(self.camera):
                shadow_surface = shadow_db.get_dungeon_shadow(
                    pokemon.sprite.shadow_size, pokemon.is_enemy
                )
                shadow_rect = shadow_surface.get_rect(
                    center=pygame.Vector2(sprite_rect.topleft)
                    + pygame.Vector2(pokemon.sprite.current_shadow_position)
                )

                floor_surface.blit(shadow_surface, shadow_rect)
                if not (
                    pokemon.status.has_status_effect(StatusEffect.DIGGING)
                    and pokemon.animation_id is AnimationId.IDLE
                ):
                    floor_surface.blit(sprite_surface, sprite_rect)

        if self.event_queue and isinstance(
            self.event_queue[0], game_event.StatAnimationEvent
        ):
            ev = self.event_queue[0]

            tile_rect.x = ev.target.moving_entity.x
            tile_rect.y = ev.target.moving_entity.y
            move_surface: pygame.Surface = ev.anim.get_current_frame()
            move_rect = move_surface.get_rect(
                bottom=tile_rect.bottom, centerx=tile_rect.centerx
            )

            if move_rect.colliderect(self.camera):
                floor_surface.blit(move_surface, move_rect)

        return floor_surface

    def get_darkness_surface(self) -> pygame.Surface:
        TILE_SIZE = self.dungeon.floor.tileset.tile_size

        surface = pygame.Surface(
            pygame.Vector2(
                self.dungeon.floor.WIDTH + 10, self.dungeon.floor.HEIGHT + 10
            ),
            pygame.SRCALPHA,
        )

        if self.dungeon.floor.status.darkness_level is DarknessLevel.NO_DARKNESS:
            surface = pygame.transform.scale_by(surface, TILE_SIZE)
            return surface.subsurface(self.camera)

        x, y = self.camera_target.position
        room_index = self.dungeon.floor[x, y].room_index

        if room_index:
            min_x = x
            while self.dungeon.floor[min_x, y].room_index == room_index:
                min_x -= 1
            max_x = x
            while self.dungeon.floor[max_x, y].room_index == room_index:
                max_x += 1
            min_y = y
            while self.dungeon.floor[x, min_y].room_index == room_index:
                min_y -= 1
            max_y = y
            while self.dungeon.floor[x, max_y].room_index == room_index:
                max_y += 1
            min_x += 5
            max_x += 6
            min_y += 5
            max_y += 6

            surface.fill((0, 0, 0, 128))
            surface.fill(
                (0, 0, 0, 0), pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)
            )
            surface = pygame.transform.scale_by(surface, TILE_SIZE)
            top_left_arc = main_db.get_darkness_quarter(0)
            top_right_arc = main_db.get_darkness_quarter(1)
            bottom_left_arc = main_db.get_darkness_quarter(2)
            bottom_right_arc = main_db.get_darkness_quarter(3)

            surface.blit(
                top_left_arc,
                top_left_arc.get_rect(topleft=(min_x * TILE_SIZE, min_y * TILE_SIZE)),
            )
            surface.blit(
                top_right_arc,
                top_right_arc.get_rect(topright=(max_x * TILE_SIZE, min_y * TILE_SIZE)),
            )
            surface.blit(
                bottom_left_arc,
                bottom_left_arc.get_rect(
                    bottomleft=(min_x * TILE_SIZE, max_y * TILE_SIZE)
                ),
            )
            surface.blit(
                bottom_right_arc,
                bottom_right_arc.get_rect(
                    bottomright=(max_x * TILE_SIZE, max_y * TILE_SIZE)
                ),
            )

        else:
            surface.fill((0, 0, 0, 128))
            surface = pygame.transform.scale_by(surface, TILE_SIZE)
            circle = main_db.get_darkness()
            hollow_square = pygame.Rect(
                (
                    self.camera.centerx - circle.get_width() // 2,
                    self.camera.centery - circle.get_height() // 2,
                ),
                circle.get_size(),
            )
            surface.fill((0, 0, 0, 0), hollow_square)
            surface.blit(circle, hollow_square)

        return surface.subsurface(self.camera)

    def get_filter_surface(self) -> pygame.Surface:
        filter_surface = pygame.Surface(
            (constants.DISPLAY_WIDTH, constants.DISPLAY_HEIGHT), pygame.SRCALPHA
        )
        filter_surface.fill(
            colormap_db.get_filter_color(self.dungeon.floor.status.weather)
        )
        return filter_surface
