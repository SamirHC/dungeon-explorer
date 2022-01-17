import battlesystem
import constants
import direction
import dungeon
import inputstream
import movementsystem
import os
import pokemon
import pygame
import pygame.image
import random
import textbox


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
    BG_DIRECTORY = os.path.join(os.getcwd(), "assets", "bg", "main")
    def __init__(self):
        super().__init__()
        self.bg = self.load_random_bg_image()
        self.menu = textbox.Menu((10, 6), [textbox.MenuOption((50, 13), "New Game"), textbox.MenuOption((50, 13), "Options")])
        self.option_description = textbox.TextBox((30, 6), 2)

    def process_input(self, input_stream: inputstream.InputStream):
        if input_stream.keyboard.is_pressed(pygame.K_s):
            self.menu.next()
        elif input_stream.keyboard.is_pressed(pygame.K_w):
            self.menu.prev()
        elif input_stream.keyboard.is_pressed(pygame.K_RETURN):
            if self.menu.pointer == 0:
                self.next_scene = DungeonScene("0", "0025")
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
    def __init__(self, dungeon_id: str, user_id: str):
        super().__init__()
        self.dungeon = dungeon.Dungeon(dungeon_id)
        self.user = pokemon.Pokemon(user_id, "User", self.dungeon)
        team = []
        team.append(self.user)
        self.dungeon.spawn_team(team)
        self.battle_system = battlesystem.BattleSystem(self.dungeon)
        self.movement_system = movementsystem.MovementSystem(self.dungeon)
        self.hud = dungeon.HUD()
        self.message_toggle = True
        self.x = constants.DISPLAY_WIDTH / 2 - self.user.blit_pos[0]
        self.y = constants.DISPLAY_HEIGHT / 2 - self.user.blit_pos[1]


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
        if self.awaiting_input():
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
            
            self.movement_system.add(sprite)
            self.movement_system.ai_move(sprite)

        if self.movement_system.moving:
            self.movement_system.update()
        elif self.battle_system.is_active:
            self.battle_system.attacker.animation.update()
            self.battle_system.update()

        if not self.movement_system.is_active and not self.battle_system.is_active:
            self.dungeon.remove_dead()
            if self.dungeon.user_is_dead():
                self.is_destroyed = True
            elif self.dungeon.user_at_stairs():
                self.dungeon.next_floor()
            elif self.user.grid_pos in self.dungeon.dungeon_map.trap_coords:
                pass

            if self.dungeon.is_next_turn():
                self.dungeon.next_turn()

        self.x = constants.DISPLAY_WIDTH / 2 - self.user.blit_pos[0]
        self.y = constants.DISPLAY_HEIGHT / 2 - self.user.blit_pos[1]

    def render(self) -> pygame.Surface:
        surface = super().render()
        # Render
        surface.fill(constants.BLACK)
        surface.blit(self.dungeon.surface, (self.x, self.y))

        # Draws sprites row by row of dungeon map
        for sprite in sorted(self.dungeon.all_sprites, key=lambda s: s.grid_pos[::-1]):
            a = sprite.blit_pos[0] + self.x
            b = sprite.blit_pos[1] + self.y
            shift_x = (sprite.current_image.get_width() -
                       constants.TILE_SIZE) // 2
            shift_y = (sprite.current_image.get_height() -
                       constants.TILE_SIZE) // 2
            surface.blit(sprite.draw(), (a - shift_x, b - shift_y))

        surface.blit(self.hud.draw(self.dungeon.is_below, self.dungeon.floor_number, self.user.level, self.user.hp, self.user.max_hp), (0, 0))
        surface.blit(self.dungeon.minimap.render(), (16, 16))
        
        if self.message_toggle:
            surface.blit(textbox.message_log.draw(), (8, 128))
        
        
        return surface
