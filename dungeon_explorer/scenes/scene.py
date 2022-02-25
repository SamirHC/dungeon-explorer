from ..dungeon import battlesystem, dungeon, hud, movementsystem
from ..common import constants, inputstream, textbox
import os
from ..pokemon import pokemon, party
import pygame
import pygame.display
import pygame.image
import pygame.mixer
import random


class Scene:
    def __init__(self):
        self.next_scene = None
        self.is_destroyed = False

    def process_input(self, input_stream: inputstream.InputStream):
        pass

    def update(self):
        pass

    def render(self) -> pygame.Surface:
        return pygame.Surface(constants.DISPLAY_SIZE)


class MainMenuScene(Scene):
    BG_DIRECTORY = os.path.join(os.getcwd(), "assets", "images", "bg", "main")
    def __init__(self):
        super().__init__()
        self.bg = self.load_random_bg_image()
        self.menu = textbox.Menu((10, 6), [textbox.MenuOption((50, 13), "New Game"), textbox.MenuOption((50, 13), "Options")])
        self.option_description = textbox.TextBox((30, 6), 2)
        pygame.mixer.music.load(os.path.join(os.getcwd(), "assets", "sound", "music", "Top Menu Theme.mp3"))
        pygame.mixer.music.play(-1)

    def process_input(self, input_stream: inputstream.InputStream):
        if input_stream.keyboard.is_pressed(pygame.K_s):
            self.menu.next()
        elif input_stream.keyboard.is_pressed(pygame.K_w):
            self.menu.prev()
        elif input_stream.keyboard.is_pressed(pygame.K_RETURN):
            if self.menu.pointer == 0:
                entry_party = party.Party()
                entry_party.add("2")
                self.next_scene = DungeonScene("1", entry_party)
                pygame.mixer.music.fadeout(500)
            else:
                print("Options")

    def update(self):
        self.menu.update()

    def render(self) -> pygame.Surface:
        surface = super().render()
        surface.blit(self.bg, (0, 0))
        surface.blit(self.menu.render(), (8, 8))
        surface.blit(self.option_description.surface, (8, 17*8))
        return surface

    def load_random_bg_image(self) -> pygame.Surface:
        file = os.path.join(MainMenuScene.BG_DIRECTORY, random.choice(os.listdir(MainMenuScene.BG_DIRECTORY)))
        return pygame.image.load(file)


class DungeonScene(Scene):
    def __init__(self, dungeon_id: str, party: list[pokemon.Pokemon]):
        super().__init__()
        self.user = party[0]
        self.dungeon = dungeon.Dungeon(dungeon_id, party)
        self.battle_system = battlesystem.BattleSystem(self.dungeon)
        self.movement_system = movementsystem.MovementSystem(self.dungeon)
        self.hud = hud.Hud(self.user, self.dungeon)
        self.message_toggle = True

    def awaiting_input(self):
        return self.user.has_turn and not self.movement_system.is_active and not self.battle_system.is_active

    def process_input(self, input_stream: inputstream.InputStream):
        # Toggle Message Log
        if input_stream.keyboard.is_pressed(pygame.K_m):
            self.message_toggle = not self.message_toggle
        # User Attack
        if self.awaiting_input():
            self.battle_system.input(input_stream)
        # User Movement
        if self.awaiting_input():
            self.movement_system.input(input_stream)

    def update(self):
        for sprite in self.dungeon.all_sprites:
            sprite.update()

        self.dungeon.tileset.update()
        self.dungeon.minimap.set_visible(self.user.position)

        if self.awaiting_input():
            for sprite in self.dungeon.all_sprites:
                sprite.animation_name = "Idle"
            return
        
        for sprite in self.dungeon.all_sprites:
            if self.battle_system.is_active:
                break
            if not sprite.has_turn:
                continue
            sprite.has_turn = False

            self.battle_system.ai_attack(sprite)
            if self.battle_system.is_active:
                break
            self.movement_system.ai_move(sprite)

        if self.movement_system.moving:
            self.movement_system.update()
        elif self.battle_system.is_active:
            self.battle_system.update()

        if not self.movement_system.is_active and not self.battle_system.is_active:
            if self.dungeon.user_is_dead():
                self.is_destroyed = True
            elif self.dungeon.user_at_stairs():
                if self.dungeon.has_next_floor():
                    self.dungeon.next_floor()
                else:
                    print("Win")
            #elif self.user.position in self.dungeon.dungeon_map.trap_coords:
            #    pass

            if self.dungeon.is_next_turn():
                self.dungeon.next_turn()

    def render(self) -> pygame.Surface:
        surface = pygame.Surface(pygame.display.get_window_size())
        display_rect = surface.get_rect()

        tile_rect = pygame.Rect(0, 0, constants.TILE_SIZE, constants.TILE_SIZE)
        if self.user in self.movement_system.moving:
            offset = pygame.Vector2(self.user.direction.value) * int(self.movement_system.movement_fraction * constants.TILE_SIZE)
        else:
            offset = pygame.Vector2(0, 0)
        tile_rect.center = pygame.Vector2(surface.get_rect().center) + offset
        dx0 = (tile_rect.x - display_rect.x) // constants.TILE_SIZE + 1
        dy0 = (tile_rect.y - display_rect.y) // constants.TILE_SIZE + 1
        w = display_rect.width // constants.TILE_SIZE + 1
        h = display_rect.height // constants.TILE_SIZE + 1
        x0 = self.user.x - dx0
        y0 = self.user.y - dy0
        x1 = x0 + w
        y1 = y0 + h
        tile_rect.x -= dx0 * constants.TILE_SIZE
        tile_rect.y -= dy0 * constants.TILE_SIZE
        tile_rect_x0, tile_rect_y0 = tile_rect.topleft
        render_range_x = range(x0, x1 + 1)
        render_range_y = range(y0, y1 + 1)
        for xi, x in enumerate(render_range_x):
            for yi, y in enumerate(render_range_y):
                tile_surface = self.dungeon.dungeonmap[x, y]
                tile_rect.x = tile_rect_x0 + constants.TILE_SIZE * xi
                tile_rect.y = tile_rect_y0 + constants.TILE_SIZE * yi
                surface.blit(tile_surface, tile_rect.topleft)

        # Draws sprites row by row of dungeon map
        for sprite in sorted(self.dungeon.all_sprites, key=lambda s: s.y):
            if sprite.x in render_range_x and sprite.y in render_range_y:
                if sprite in self.movement_system.moving:
                    offset = pygame.Vector2(sprite.direction.value) * int(self.movement_system.movement_fraction * constants.TILE_SIZE)
                else:
                    offset = pygame.Vector2(0, 0)
                tile_rect.x = tile_rect_x0 + constants.TILE_SIZE * (sprite.x - x0) - offset.x
                tile_rect.y = tile_rect_y0 + constants.TILE_SIZE * (sprite.y - y0) - offset.y
                sprite_surface = sprite.render()
                sprite_rect = sprite_surface.get_rect(center=tile_rect.center)
                surface.blit(sprite_surface, sprite_rect)

        surface.blit(self.hud.render(), (0, 0))
        surface.blit(self.dungeon.minimap.render(self.user.position, [s.position for s in self.dungeon.active_enemies]), (0, 0))
        if self.message_toggle:
            surface.blit(self.dungeon.message_log.draw(), (8, 128))

        return surface
