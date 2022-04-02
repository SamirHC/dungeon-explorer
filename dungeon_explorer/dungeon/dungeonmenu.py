import pygame

from dungeon_explorer.common import inputstream, menu, constants, text, textbox
from dungeon_explorer.dungeon import dungeon
from dungeon_explorer.pokemon import party, pokemon, move, pokemondata


class MoveMenu:
    def __init__(self, party: party.Party):
        self.party = party
        self.frame = textbox.Frame((20, 14)).with_header_divider().with_footer_divider()
        self.menu = menu.PagedMenuModel([[m.name for m in p.moveset] for p in self.party])
        self.frozen = False

    @property
    def page(self) -> int:
        return self.menu.page

    @property
    def pointer(self) -> int:
        return self.menu.pointer

    @property
    def target_pokemon(self) -> pokemon.Pokemon:
        return self.party[self.menu.page]

    @property
    def target_moveset(self) -> pokemondata.Moveset:
        return self.target_pokemon.moveset

    @property
    def target_move(self) -> move.Move:
        return self.target_moveset[self.pointer]

    @property
    def display_page(self) -> int:
        return self.menu.page + 1

    def shift_up(self):
        self.menu.pointer = self.target_moveset.shift_up(self.pointer)

    def shift_down(self):
        self.menu.pointer = self.target_moveset.shift_down(self.pointer)

    def process_input(self, input_stream: inputstream.InputStream):
        kb = input_stream.keyboard
        if kb.is_pressed(pygame.K_s):
            menu.pointer_animation.restart()
            self.menu.next()
        elif kb.is_pressed(pygame.K_w):
            menu.pointer_animation.restart()
            self.menu.prev()
        elif kb.is_pressed(pygame.K_d):
            menu.pointer_animation.restart()
            self.menu.next_page()
        elif kb.is_pressed(pygame.K_a):
            menu.pointer_animation.restart()
            self.menu.prev_page()
        elif kb.is_pressed(pygame.K_RETURN):
            print(self.target_move.name)

    def update(self):
        menu.pointer_animation.update()

    def render(self):
        self.surface = pygame.Surface(self.frame.get_size(), pygame.SRCALPHA)
        self.render_frame()
        self.render_title()
        self.render_page_num()
        self.render_move_dividers()
        self.render_move_name_pp()
        self.render_pointer()
        return self.surface

    def render_frame(self):
        self.surface.blit(self.frame, (0, 0))

    def render_title(self):
        title = text.build_multicolor([(f"  {self.target_pokemon.name}", self.target_pokemon.name_color),("'s moves", constants.OFF_WHITE)])
        self.surface.blit(title, self.frame.container_rect.topleft)

    def render_page_num(self):
        end = pygame.Vector2(self.surface.get_width()-8, 8)
        page_num_surface = text.build(f"({self.display_page}/{len(self.party)})")
        page_num_rect = page_num_surface.get_rect(topright=end)
        self.surface.blit(page_num_surface, page_num_rect.topleft)

    def render_move_dividers(self):
        start = pygame.Vector2(16, 16) + pygame.Vector2(8, 8)
        move_divider = text.text_divider(127)
        num_move_dividers = len(self.target_moveset) - 1
        for i in range(num_move_dividers):
            start += pygame.Vector2(0, 16)
            self.surface.blit(move_divider, start)

    def render_move_name_pp(self):
        start = pygame.Vector2(16, 18) + self.frame.container_rect.topleft
        end = pygame.Vector2(-4, 18) + self.frame.container_rect.topright
        for i in range(len(self.target_moveset)):
            move = self.target_moveset[i]
            pp_left = self.target_moveset.pp[i]
            color = constants.GREEN if pp_left else constants.RED
            
            self.surface.blit(text.build(move.name, color), start)
            start += pygame.Vector2(0, 16)

            pp_surface = text.build(f"{pp_left}/{move.pp}", color)
            pp_rect = pp_surface.get_rect(topright=end)
            self.surface.blit(pp_surface, pp_rect.topleft)
            end += pygame.Vector2(0, 16)

    def render_pointer(self):
        if self.frozen:
            surf = menu.pointer_surface
        else:
            surf = menu.pointer_animation.render()
        pointer_position = pygame.Vector2(self.frame.container_rect.topleft) + pygame.Vector2(0, 18) + pygame.Vector2(0, 16)*self.menu.pointer
        self.surface.blit(surf, pointer_position)


class DungeonMenu:
    def __init__(self, dungeon: dungeon.Dungeon):
        self.dungeon = dungeon

        # Top Menu
        self.top_menu = menu.Menu((8, 14), ["Moves", "Items", "Team", "Others", "Ground", "Rest", "Exit"])
        self.dungeon_title = self.get_title_surface()

        # Moves
        self.moves_menu = MoveMenu(dungeon.party)
        self.moves_submenu = menu.Menu((10, 13), ["Use", "Set", "Shift Up", "Shift Down", "Info", "Exit"])

        self.current_menu = None
    
    @property
    def is_active(self) -> bool:
        return self.current_menu is not None
    
    def get_title_surface(self) -> pygame.Surface:
        title = text.build(self.dungeon.dungeon_data.name, constants.GOLD)
        surface = textbox.Frame((21, 4))
        rect = title.get_rect(center=surface.get_rect().center)
        surface.blit(title, rect.topleft)
        return surface

    def get_party_status_surface(self) -> pygame.Surface:
        frame = textbox.Frame((30, 8))
        # Render names/hp
        start = frame.container_rect.topleft
        end = pygame.Vector2(117, 8)
        for p in self.dungeon.party:
            name_surf = text.build(f" {p.name}", p.name_color)
            frame.blit(name_surf, start)
            start += pygame.Vector2(0, 12)
            hp_surf = text.build(f"{p.hp_status: >3}/{p.hp: >3}")
            hp_rect = hp_surf.get_rect(topright=end)
            frame.blit(hp_surf, hp_rect.topleft)
            end += pygame.Vector2(0, 12)

        return frame

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
    
    def render(self) -> pygame.Surface:
        self.surface = pygame.Surface(constants.DISPLAY_SIZE, pygame.SRCALPHA)
        if self.current_menu is self.top_menu:
            return self.render_top_menu()
        elif self.current_menu is self.moves_menu:
            return self.render_moves_menu()
        elif self.current_menu is self.moves_submenu:
            return self.render_moves_submenu()
        return self.surface

    def render_top_menu(self) -> pygame.Surface:
        self.surface.blit(self.top_menu.render(), (8, 8))
        self.surface.blit(self.dungeon_title, (80, 24))
        self.surface.blit(self.get_party_status_surface(), (8, 120))
        return self.surface

    def render_moves_menu(self) -> pygame.Surface:
        self.surface.blit(self.moves_menu.render(), (8, 8))
        return self.surface

    def render_moves_submenu(self) -> pygame.Surface:
        self.surface = self.render_moves_menu()
        self.surface.blit(self.moves_submenu.render(), (168, 8))
        return self.surface
