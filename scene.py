import battlesystem
import constants
import direction
import dungeon
import keyboard
import pokemon
import pygame
import random
import time
import textbox

class Scene:
    def __init__(self):
        pass
    def process_input(self, keyboard_input):
        pass
    def update(self):
        pass
    def render(self):
        pass

class DungeonScene(Scene):
    def __init__(self, dungeon_id, user_id):
        self.dungeon = dungeon.Dungeon(dungeon_id)
        self.user = pokemon.Pokemon(user_id, "User", self.dungeon)
        team = []
        team.append(self.user)
        self.dungeon.spawn_team(team)
        self.battle_system = battlesystem.BattleSystem(self.dungeon)
        self.motion = False
        self.in_battle = False
        self.message_toggle = True
        self.time_for_one_tile = constants.TIME_FOR_ONE_TILE
        self.motion_time_left = 0
        self.t = time.time()
        self.display = pygame.Surface((constants.DISPLAY_WIDTH, constants.DISPLAY_HEIGHT))

    def process_input(self, keyboard_input: keyboard.Keyboard):
        # Input
        # Toggle Message Log
        if keyboard_input.is_pressed(pygame.K_m):
            self.message_toggle = not self.message_toggle

        if self.user.has_turn and not self.motion_time_left and not self.in_battle:
            # User Attack
            self.battle_system.set_attacker(self.user)
            for key in constants.attack_keys:
                if keyboard_input.is_pressed(key):
                    if self.battle_system.activate_by_key(key):
                        self.in_battle = True
                        self.battle_system.attacker.set_attack_animation(self.battle_system.current_move)
                        self.battle_system.attacker.animation.start()

        if self.user.has_turn and not self.motion_time_left and not self.in_battle:
            # Sprint
            if keyboard_input.is_held(pygame.K_LSHIFT):
                self.time_for_one_tile = constants.FASTER_TIME_FOR_ONE_TILE
            else:
                self.time_for_one_tile = constants.TIME_FOR_ONE_TILE

            # User Movement
            for key in constants.direction_keys:
                if keyboard_input.is_pressed(key) or keyboard_input.is_held(key):
                    self.user.direction = constants.direction_keys[key]
                    self.user.animation_name = "Walk"
                    if self.user.direction in self.user.possible_directions():
                        self.user.move_on_grid(None)
                        self.user.has_turn = False
                        self.motion = True
                    break  # Only one direction need be processed

    def update(self):
        # Update
        if not self.user.has_turn and not self.motion_time_left and not self.in_battle:  # Enemy Attack Phase
            for enemy in self.dungeon.active_enemies:
                self.battle_system.set_attacker(enemy)
                if enemy.has_turn:
                    if 1 <= enemy.distance_to(self.user.grid_pos) < 2:  # If the enemy is adjacent to the user
                        enemy.move_in_direction_of_minimal_distance(self.user, list(direction.Direction))  # Faces user
                        enemy.animation_name = "Walk"

                        possible_attack_indices = self.battle_system.possible_moves()
                        if possible_attack_indices:
                            m = random.choice(possible_attack_indices)
                        else:
                            m = None
                            break
                        
                        if self.battle_system.activate(m):
                            self.in_battle = True
                            self.battle_system.attacker.set_attack_animation(self.battle_system.current_move)
                            self.battle_system.attacker.animation.start()
                        break
        
        if not self.user.has_turn and not self.motion_time_left and not self.in_battle:  # Enemy Movement Phase
            for enemy in [s for s in self.dungeon.active_enemies if s.has_turn]:
                enemy.move_on_grid(self.user)  # Otherwise, just move the position of the enemy
                enemy.has_turn = False
                self.motion = True

        if self.motion:
            self.motion = False
            self.old_time = time.time()
            self.motion_time_left = self.time_for_one_tile  # Resets timer

        if self.motion_time_left > 0:
            self.t = time.time() - self.old_time
            self.old_time = time.time()
            self.motion_time_left = max(self.motion_time_left - self.t, 0)

            for sprite in self.dungeon.all_sprites:
                sprite.motion_animation(self.motion_time_left, self.time_for_one_tile)

        elif self.in_battle:
            self.battle_system.attacker.animation.update()

            if self.battle_system.attacker.animation.iterations and self.battle_system.steps:
                self.battle_system.attacker.animation_name = "Walk"
                if self.battle_system.target_index + 1 != len(self.battle_system.steps[self.battle_system.step_index]["Targets"]):
                    self.battle_system.target_index += 1
                    self.battle_system.attacker.animation.start()
                elif self.battle_system.step_index + 1 != len(self.battle_system.steps):
                    self.battle_system.step_index += 1
                    self.battle_system.target_index = 0
                    self.battle_system.attacker.animation.start()
                else:
                    self.battle_system.attacker.has_turn = False
                    self.in_battle = False
            elif self.battle_system.attacker.animation.iterations:
                self.battle_system.attacker.animation_name = "Walk"
                self.in_battle = False

        if self.motion_time_left == 0 and not self.in_battle:
            self.dungeon.remove_dead()
            if self.dungeon.user_is_dead():
                running = False
            elif self.dungeon.user_at_stairs():
                self.dungeon.next_floor()
            elif self.user.grid_pos in self.dungeon.dungeon_map.trap_coords:
                pass

            if self.dungeon.is_next_turn():
                self.dungeon.next_turn()

        if self.motion_time_left == 0:
            self.x = constants.DISPLAY_WIDTH / 2 - self.user.grid_pos[0] * constants.TILE_SIZE
            self.y = constants.DISPLAY_HEIGHT / 2 - self.user.grid_pos[1] * constants.TILE_SIZE
        else:
            self.x = constants.DISPLAY_WIDTH / 2 - self.user.blit_pos[0]
            self.y = constants.DISPLAY_HEIGHT / 2 - self.user.blit_pos[1]

    def render(self):
        # Render
        self.display.fill(constants.BLACK)
        self.display.blit(self.dungeon.surface, (self.x, self.y))

        # Draws sprites row by row of dungeon map
        for sprite in sorted(self.dungeon.all_sprites, key=lambda s: s.grid_pos[::-1]):
            a = sprite.blit_pos[0] + self.x
            b = sprite.blit_pos[1] + self.y
            shift_x = (sprite.current_image.get_width() - constants.TILE_SIZE) // 2
            shift_y = (sprite.current_image.get_height() - constants.TILE_SIZE) // 2
            self.display.blit(sprite.draw(), (a - shift_x, b - shift_y))

        self.display.blit(self.dungeon.draw_hud(), (0, 0))

        if self.message_toggle:
            self.display.blit(textbox.message_log.draw(), textbox.message_log.rect.topleft)
