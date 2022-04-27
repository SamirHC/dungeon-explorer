import pygame

from dungeon_explorer.common import inputstream, menu, constants, text, textbox
from dungeon_explorer.dungeon import battlesystem, dungeon
from dungeon_explorer.pokemon import party, pokemon, move, pokemondata


MENU_ALPHA = 128


class MoveMenu:
    def __init__(self, party: party.Party, battle_system: battlesystem.BattleSystem):
        self.party = party
        self.battle_system = battle_system
        self.frame = textbox.Frame((20, 14), MENU_ALPHA).with_header_divider().with_footer_divider()
        self.menu = menu.PagedMenuModel([[m.name for m in p.moveset] for p in self.party])
        self.submenu = menu.Menu((10, 13), ["Use", "Set", "Shift Up", "Shift Down", "Info", "Exit"], MENU_ALPHA)
        self.is_submenu_active = False

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
        if self.is_submenu_active:
            self.process_input_submenu(input_stream)
        else:
            self.process_input_menu(input_stream)

    def process_input_menu(self, input_stream: inputstream.InputStream):
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
            if self.target_pokemon is self.party.leader:
                self.is_submenu_active = True
                menu.pointer_animation.restart()

    def process_input_submenu(self, input_stream: inputstream.InputStream):
        self.submenu.process_input(input_stream)
        if input_stream.keyboard.is_pressed(pygame.K_RETURN):
            if not self.submenu.is_active_option:
                return
            if self.submenu.current_option == "Use":
                self.battle_system.attacker = self.party.leader
                self.battle_system.activate(self.menu.pointer)
            elif self.submenu.current_option == "Set":
                print("Set not implemented")
            elif self.submenu.current_option == "Shift Up":
                self.shift_up()
            elif self.submenu.current_option == "Shift Down":
                self.shift_down()
            elif self.submenu.current_option == "Info":
                print("Info not implemented")
            self.submenu.pointer = 0
            self.is_submenu_active = False
            menu.pointer_animation.restart()

    def update(self):
        menu.pointer_animation.update()
        if self.is_submenu_active:
            self.submenu.active[0] = self.target_moveset.can_use(self.pointer)
            self.submenu.active[2] = self.pointer != 0
            self.submenu.active[3] = self.pointer != len(self.target_moveset) - 1        

    def render(self):
        self.render_menu_surface()
        if not self.is_submenu_active:
            return self.menu_surface
        self.render_submenu()
        return self.render_combined_surface()

    def render_combined_surface(self):
        combined_width = self.frame.get_width()+self.submenu.textbox_frame.get_width()
        combined_height = self.frame.get_height()
        combined_surface = pygame.Surface((combined_width, combined_height), pygame.SRCALPHA)
        combined_surface.blit(self.menu_surface, (0, 0))
        combined_surface.blit(self.submenu_surface, (160, 0))
        return combined_surface

    def render_menu_surface(self):
        self.menu_surface = pygame.Surface(self.frame.get_size(), pygame.SRCALPHA)
        self.render_frame()
        self.render_title()
        self.render_page_num()
        self.render_move_dividers()
        self.render_move_name_pp()
        self.render_pointer()
        return self.menu_surface

    def render_frame(self):
        self.menu_surface.blit(self.frame, (0, 0))

    def render_title(self):
        title = (
            text.TextBuilder()
            .set_shadow(True)
            .write(f"  {self.target_pokemon.name}", self.target_pokemon.name_color)
            .write("'s moves")
            .build()
        )
        self.menu_surface.blit(title, self.frame.container_rect.topleft)

    def render_page_num(self):
        end = pygame.Vector2(self.menu_surface.get_width()-8, 8)
        page_num_surface = (
            text.TextBuilder()
            .set_shadow(True)
            .write(f"({self.display_page}/{len(self.party)})")
            .build()
        )
        page_num_rect = page_num_surface.get_rect(topright=end)
        self.menu_surface.blit(page_num_surface, page_num_rect.topleft)

    def render_move_dividers(self):
        start = pygame.Vector2(16, 16) + pygame.Vector2(8, 8)
        move_divider = text.divider(127)
        num_move_dividers = len(self.target_moveset) - 1
        for i in range(num_move_dividers):
            start += pygame.Vector2(0, 16)
            self.menu_surface.blit(move_divider, start)

    def render_move_name_pp(self):
        start = pygame.Vector2(16, 18) + self.frame.container_rect.topleft
        end = pygame.Vector2(-4, 18) + self.frame.container_rect.topright
        for i in range(len(self.target_moveset)):
            move = self.target_moveset[i]
            pp_left = self.target_moveset.pp[i]
            color = constants.GREEN if pp_left else constants.RED
            move_name_surface = (
                text.TextBuilder()
                .set_shadow(True)
                .write(move.name, color)
                .build()
            )
            self.menu_surface.blit(move_name_surface, start)
            start += pygame.Vector2(0, 16)

            pp_surface = (
                text.TextBuilder()
                .set_shadow(True)
                .write(f"{pp_left}/{move.pp}", color)
                .build()
            )
            pp_rect = pp_surface.get_rect(topright=end)
            self.menu_surface.blit(pp_surface, pp_rect.topleft)
            end += pygame.Vector2(0, 16)

    def render_pointer(self):
        if self.is_submenu_active:
            surf = menu.pointer_surface
        else:
            surf = menu.pointer_animation.render()
        pointer_position = pygame.Vector2(self.frame.container_rect.topleft) + pygame.Vector2(0, 18) + pygame.Vector2(0, 16)*self.menu.pointer
        self.menu_surface.blit(surf, pointer_position)

    def render_submenu(self):
        self.submenu_surface = self.submenu.render()


class StairsMenu:
    def __init__(self):
        self.menu = menu.Menu((9, 8), ["Proceed", "Info", "Cancel"], 128)
        self.frame = self.build_stairs_surface()
        self.auto = False
        self.proceed = False
        self.cancelled = False
        
    def build_stairs_surface(self) -> pygame.Surface:
        surface = textbox.Frame((21, 6), 128).with_header_divider()
        stairs_text_surface = (
            text.TextBuilder()
            .set_shadow(True)
            .write("Stairs")
            .build()
        )
        surface.blit(stairs_text_surface, (16, 10))
        surface.blit(stairs_text_surface, (24, 28))
        return surface

    def process_input(self, input_stream: inputstream.InputStream):
        self.menu.process_input(input_stream)
    
    def update(self):
        self.menu.update()

    def render(self) -> pygame.Surface:
        surface = pygame.Surface(constants.DISPLAY_SIZE, pygame.SRCALPHA)
        surface.blit(self.frame, (8, 8))
        surface.blit(self.menu.render(), (176, 8))
        return surface


class DungeonMenu:
    def __init__(self, dungeon: dungeon.Dungeon, battle_system: battlesystem.BattleSystem):
        self.dungeon = dungeon

        # Top Menu
        self.top_menu = menu.Menu((8, 14), ["Moves", "Items", "Team", "Others", "Ground", "Rest", "Exit"], MENU_ALPHA)
        self.dungeon_title = self.get_title_surface()

        # Moves
        self.moves_menu = MoveMenu(dungeon.party, battle_system)

        # Ground
        self.stairs_menu = StairsMenu()

        self.current_menu = None
    
    @property
    def is_active(self) -> bool:
        return self.current_menu is not None
    
    def get_title_surface(self) -> pygame.Surface:
        title = (
            text.TextBuilder()
            .set_shadow(True)
            .write(self.dungeon.dungeon_data.name, constants.GOLD)
            .build()
        )
        surface = textbox.Frame((21, 4), MENU_ALPHA)
        rect = title.get_rect(center=surface.get_rect().center)
        surface.blit(title, rect.topleft)
        return surface

    def get_party_status_surface(self) -> pygame.Surface:
        frame = textbox.Frame((30, 8), MENU_ALPHA)
        # Render names/hp
        start = frame.container_rect.topleft
        end = pygame.Vector2(117, 8)
        for p in self.dungeon.party:
            name_surf = (
                text.TextBuilder()
                .set_shadow(True)
                .write(f" {p.name}", p.name_color)
                .build()
            )
            frame.blit(name_surf, start)
            start += pygame.Vector2(0, 12)
            hp_surf = (
                text.TextBuilder()
                .set_shadow(True)
                .write(f"{p.hp_status: >3}/{p.hp: >3}")
                .build()
            )
            hp_rect = hp_surf.get_rect(topright=end)
            frame.blit(hp_surf, hp_rect.topleft)
            end += pygame.Vector2(0, 12)

        return frame

    def process_input(self, input_stream: inputstream.InputStream):
        if input_stream.keyboard.is_pressed(pygame.K_n):
            self.moves_menu.is_submenu_active = False
            if self.current_menu is not self.top_menu:
                self.current_menu = self.top_menu
            else:
                self.current_menu = None
        elif self.current_menu is self.top_menu:
            self.process_input_top_menu(input_stream)
        elif self.current_menu is self.moves_menu:
            self.process_input_moves_menu(input_stream)
        elif self.current_menu is self.stairs_menu:
            self.process_input_stairs_menu(input_stream)

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
                print("Ground not fully implemented")
                if self.dungeon.user_at_stairs():
                    self.current_menu = self.stairs_menu
                    self.stairs_menu.auto = False
            elif self.top_menu.current_option == "Rest":
                print("Rest not implemented")
            elif self.top_menu.current_option == "Exit":
                self.current_menu = None

    def process_input_moves_menu(self, input_stream: inputstream.InputStream):
        self.moves_menu.process_input(input_stream)

    def process_input_stairs_menu(self, input_stream: inputstream.InputStream):
        self.stairs_menu.process_input(input_stream)
        if input_stream.keyboard.is_pressed(pygame.K_RETURN):
            curr = self.stairs_menu.menu.current_option
            if curr == "Proceed":
                self.stairs_menu.proceed = True
            elif curr == "Info":
                print("Stairs leading to the next floor. If you are on\nthe final floor, you will escape from the\ndungeon.")
            elif curr == "Cancel":
                self.stairs_menu.cancelled = True
                if self.stairs_menu.auto:
                    self.current_menu = None
                else:
                    self.current_menu = self.top_menu

    def update(self):
        if self.moves_menu.battle_system.is_active:
            self.current_menu = None
        elif self.current_menu is self.top_menu:
            self.update_top_menu()
        elif self.current_menu is self.moves_menu:
            self.update_moves_menu()
        elif self.current_menu is self.stairs_menu:
            self.stairs_menu.update()
    
    def update_top_menu(self):
        self.top_menu.update()

    def update_moves_menu(self):
        self.moves_menu.update()
    
    def render(self) -> pygame.Surface:
        self.surface = pygame.Surface(constants.DISPLAY_SIZE, pygame.SRCALPHA)
        if self.current_menu is self.top_menu:
            return self.render_top_menu()
        elif self.current_menu is self.moves_menu:
            return self.render_moves_menu()
        elif self.current_menu is self.stairs_menu:
            return self.stairs_menu.render()
        return self.surface

    def render_top_menu(self) -> pygame.Surface:
        self.surface.blit(self.top_menu.render(), (8, 8))
        self.surface.blit(self.dungeon_title, (80, 24))
        self.surface.blit(self.get_party_status_surface(), (8, 120))
        return self.surface

    def render_moves_menu(self) -> pygame.Surface:
        self.surface.blit(self.moves_menu.render(), (8, 8))
        return self.surface
