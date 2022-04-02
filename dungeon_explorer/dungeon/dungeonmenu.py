import pygame

from dungeon_explorer.common import inputstream, menu, constants, text, textbox
from dungeon_explorer.dungeon import dungeon


class DungeonMenu:
    def __init__(self, dungeon: dungeon.Dungeon):
        self.dungeon = dungeon

        # Top Menu
        self.top_menu = menu.Menu((8, 14), ["Moves", "Items", "Team", "Others", "Ground", "Rest", "Exit"])
        self.dungeon_title = self.get_title_surface()

        # Moves
        self.moves_menu = menu.MoveMenu(dungeon.party)
        self.moves_submenu = menu.Menu((10, 13), ["Use", "Set", "Shift Up", "Shift Down", "Info", "Exit"])

        self.current_menu = None
    
    @property
    def is_active(self) -> bool:
        return self.current_menu is not None
    
    def get_title_surface(self):
        title = text.build(self.dungeon.dungeon_data.name, constants.GOLD)
        surface = textbox.Frame((21, 4))
        rect = title.get_rect(center=surface.get_rect().center)
        surface.blit(title, rect.topleft)
        return surface

    def process_input(self, input_stream: inputstream.InputStream):
        if input_stream.keyboard.is_pressed(pygame.K_n):
            if self.current_menu is not self.top_menu:
                self.current_menu = self.top_menu
            else:
                self.current_menu = None
            return
        if self.current_menu is self.top_menu:
            self.process_input_top_menu(input_stream)
            return
        if self.current_menu is self.moves_menu:
            self.process_input_moves_menu(input_stream)
            return
        if self.current_menu is self.moves_submenu:
            self.process_input_moves_submenu(input_stream)

    def process_input_top_menu(self, input_stream: inputstream.InputStream):
        self.top_menu.process_input(input_stream)
        if input_stream.keyboard.is_pressed(pygame.K_RETURN):
            if self.top_menu.current_option == "Moves":
                self.current_menu = self.moves_menu
            elif self.top_menu.current_option == "Items":
                print("Items not implemented")
            elif self.top_menu.current_option == "Team":
                for p in self.dungeon.party:
                    print(p.name, p.hp_status)
            elif self.top_menu.current_option == "Others":
                print("Others not implemented")
            elif self.top_menu.current_option == "Ground":
                print("Ground not implemented")
            elif self.top_menu.current_option == "Rest":
                print("Rest not implemented")
            elif self.top_menu.current_option == "Exit":
                self.current_menu = None

    def process_input_moves_menu(self, input_stream: inputstream.InputStream):
        self.moves_menu.process_input(input_stream)
        if input_stream.keyboard.is_pressed(pygame.K_RETURN):
            self.current_menu = self.moves_submenu
            self.moves_menu.frozen = True
            menu.pointer_animation.restart()

    def process_input_moves_submenu(self, input_stream: inputstream.InputStream):
        self.moves_submenu.process_input(input_stream)
        if input_stream.keyboard.is_pressed(pygame.K_RETURN):
            if self.moves_submenu.current_option == "Use":
                print("Use not implemented")
            elif self.moves_submenu.current_option == "Set":
                print("Set not implemented")
            elif self.moves_submenu.current_option == "Shift Up":
                self.moves_menu.shift_up()
            elif self.moves_submenu.current_option == "Shift Down":
                self.moves_menu.shift_down()
            elif self.moves_submenu.current_option == "Info":
                print("Info not implemented")
            self.moves_submenu.pointer = 0
            self.current_menu = self.moves_menu
            self.moves_menu.frozen = False
            menu.pointer_animation.restart()

    def update(self):
        if self.current_menu is self.top_menu:
            return self.update_top_menu()
        elif self.current_menu is self.moves_menu:
            return self.update_moves_menu()
        elif self.current_menu is self.moves_submenu:
            return self.update_moves_submenu()
        
    def update_top_menu(self):
        self.top_menu.update()

    def update_moves_menu(self):
        self.moves_menu.update()

    def update_moves_submenu(self):
        self.moves_submenu.update()
    
    def render(self):
        self.surface = pygame.Surface(constants.DISPLAY_SIZE, pygame.SRCALPHA)
        if self.current_menu is self.top_menu:
            return self.render_top_menu()
        elif self.current_menu is self.moves_menu:
            return self.render_moves_menu()
        elif self.current_menu is self.moves_submenu:
            return self.render_moves_submenu()
        return self.surface

    def render_top_menu(self):
        self.surface.blit(self.top_menu.render(), (8, 8))
        self.surface.blit(self.dungeon_title, (80, 24))
        return self.surface

    def render_moves_menu(self):
        self.surface.blit(self.moves_menu.render(), (8, 8))
        return self.surface

    def render_moves_submenu(self):
        self.surface = self.render_moves_menu()
        self.surface.blit(self.moves_submenu.render(), (168, 8))
        return self.surface
