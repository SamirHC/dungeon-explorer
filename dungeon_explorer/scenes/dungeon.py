import pygame
import pygame.display
import pygame.image
import pygame.mixer
from dungeon_explorer.common import constants, inputstream, menu, text, textbox
from dungeon_explorer.dungeon import battlesystem, dungeon, dungeonmap, dungeondata, minimap, hud, movementsystem
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

        self.dungeon_name_banner = text.banner_font.render(dungeon_data.banner)
        self.floor_num_banner = text.banner_font.render(self.floor_string)

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
        self.weather_filter = self.dungeon.status.weather.colormap()
        self.hud = hud.Hud(self.user, self.dungeon)
        self.message_toggle = True
        
        # Main Dungeon Menu
        self.menu_toggle = False
        self.menu = menu.Menu((8, 14), ["Moves", "Items", "Team", "Others", "Ground", "Rest", "Exit"])
        self.dungeon_title = self.get_title_surface()
        # Move Menu
        self.move_menu_toggle = False
        self.move_menu = menu.MoveMenu(self.dungeon.party)
        # Move Sub Menu
        self.move_submenu_toggle = False
        self.move_submenu = menu.Menu((10, 13), ["Use", "Set", "Shift Up", "Shift Down", "Info", "Exit"])


    def get_title_surface(self):
        title = text.build(self.dungeon.dungeon_data.name, constants.GOLD)
        surface = textbox.Frame((21, 4))
        rect = title.get_rect(center=surface.get_rect().center)
        surface.blit(title, rect.topleft)
        return surface

    def awaiting_input(self):
        return self.user.has_turn and not self.movement_system.is_active and not self.battle_system.is_active

    def in_menu(self):
        return self.menu_toggle or self.move_menu_toggle or self.move_submenu_toggle

    def process_input(self, input_stream: inputstream.InputStream):
        # Toggle Menu
        if self.awaiting_input():
            if input_stream.keyboard.is_pressed(pygame.K_n):
                self.menu_toggle = not self.menu_toggle
                self.move_menu_toggle = False
                self.move_submenu_toggle = False
        # Menu
        if self.menu_toggle:
            self.menu.process_input(input_stream)
            if input_stream.keyboard.is_pressed(pygame.K_RETURN):
                if self.menu.current_option == "Moves":
                    self.move_menu_toggle = True
                    self.move_menu.render()
                    self.menu_toggle = False
                elif self.menu.current_option == "Items":
                    print("Items not implemented")
                elif self.menu.current_option == "Team":
                    for p in self.dungeon.party:
                        print(p.name, p.hp_status)
                elif self.menu.current_option == "Others":
                    print("Others not implemented")
                elif self.menu.current_option == "Ground":
                    print("Ground not implemented")
                elif self.menu.current_option == "Rest":
                    print("Rest not implemented")
                elif self.menu.current_option == "Exit":
                    self.menu_toggle = False
            return
        # Move Menu
        if self.move_menu_toggle:
            self.move_menu.process_input(input_stream)
            if input_stream.keyboard.is_pressed(pygame.K_RETURN):
                self.move_menu_toggle = False
                self.move_submenu_toggle = True
            return
        # Move Sub Menu
        if self.move_submenu_toggle:
            self.move_submenu.process_input(input_stream)
            if input_stream.keyboard.is_pressed(pygame.K_RETURN):
                if self.move_submenu.current_option == "Use":
                    print("Use not implemented")
                elif self.move_submenu.current_option == "Set":
                    print("Set not implemented")
                elif self.move_submenu.current_option == "Shift Up":
                    self.move_menu.shift_up()
                    self.move_submenu.pointer = 0
                    self.move_menu_toggle = True
                    self.move_submenu_toggle = False
                elif self.move_submenu.current_option == "Shift Down":
                    self.move_menu.shift_down()
                    self.move_submenu.pointer = 0
                    self.move_menu_toggle = True
                    self.move_submenu_toggle = False
                elif self.move_submenu.current_option == "Info":
                    print("Info not implemented")
                elif self.move_submenu.current_option == "Exit":
                    self.move_submenu.pointer = 0
                    self.move_menu_toggle = True
                    self.move_submenu_toggle = False
            return
        # Toggle Message Log
        if input_stream.keyboard.is_pressed(pygame.K_m):
            self.message_toggle = not self.message_toggle
        # User Attack
        if self.awaiting_input() and not self.menu_toggle:
            self.battle_system.input(input_stream)
        # User Movement
        if self.awaiting_input() and not self.menu_toggle:
            self.movement_system.input(input_stream)

    def update(self):
        for sprite in self.dungeon.all_sprites:
            sprite.update()

        self.dungeon.tileset.update()
        self.minimap.set_visible(self.user.position)
    
        if self.menu_toggle:
            self.menu.update()
        elif self.move_menu_toggle:
            self.move_menu.update()
        elif self.move_submenu_toggle:
            self.move_submenu.update()

        if self.awaiting_input() or self.in_menu():
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
                self.next_scene = mainmenu.MainMenuScene()
            elif self.dungeon.user_at_stairs():
                if self.dungeon.has_next_floor():
                    self.next_scene = FloorTransitionScene(self.dungeon.dungeon_data, self.dungeon.floor_number+1, self.dungeon.party)
                else:
                    self.next_scene = mainmenu.MainMenuScene()

            if self.dungeon.is_next_turn():
                self.dungeon.next_turn()

    def render(self) -> pygame.Surface:
        surface = pygame.Surface(constants.DISPLAY_SIZE)
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
                tile_surface = self.dungeonmap[x, y]
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

        if self.menu_toggle:
            surface.blit(self.menu.render(), (8, 8))
            surface.blit(self.dungeon_title, (80, 24))
            return surface
        elif self.move_menu_toggle:
            surface.blit(self.move_menu.render(), (8, 8))
            return surface
        elif self.move_submenu_toggle:
            surface.blit(self.move_menu.surface, (8, 8))
            surface.blit(self.move_submenu.render(), (168, 8))
            return surface

        surface.blit(self.minimap.render(), (0, 0))
        if self.message_toggle:
            surface.blit(self.dungeon.message_log.draw(), (8, 128))

        return surface
