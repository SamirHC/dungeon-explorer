import battlesystem
import constants
import direction
import dungeon
import keyboard
import pokemon
import pygame
import pygame.display
import pygame.draw
import pygame.event
import pygame.key
import pygame.time
import random
import time
import textbox

# Initialisation
pygame.init()
display = pygame.display.set_mode((constants.DISPLAY_WIDTH, constants.DISPLAY_HEIGHT))
pygame.display.set_caption(constants.CAPTION)
clock = pygame.time.Clock()
keyboard_input = keyboard.Keyboard()
battle_system = battlesystem.BattleSystem()

dungeon_id = "BeachCave"
user_id = "0025"
d = dungeon.Dungeon(dungeon_id)

team = []
user = pokemon.Pokemon(user_id, "User", d)
team.append(user)
d.spawn_team(team)

motion = False
message_toggle = True
time_for_one_tile = constants.TIME_FOR_ONE_TILE
motion_time_left = 0
attack_time_left = 0
t = time.time()

# Game loop
running = True
while running:
    # Input
    # Gets the keyboard state
    keyboard_input.update()

    # Checks if user quits
    for event in pygame.event.get():
        if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

    # Toggle Fullscreen
    if keyboard_input.is_pressed(pygame.K_F11):
        if display.get_flags() & pygame.FULLSCREEN:
            pygame.display.set_mode((constants.DISPLAY_WIDTH, constants.DISPLAY_HEIGHT))
        else:
            pygame.display.set_mode((constants.DISPLAY_WIDTH, constants.DISPLAY_HEIGHT), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
    
    # Toggle Message Log
    if keyboard_input.is_pressed(pygame.K_m):
        message_toggle = not message_toggle

    if user.has_turn and not motion_time_left and not attack_time_left:
        # User Attack
        for key in constants.attack_keys:
            if keyboard_input.is_pressed(key):
                attack_index = constants.attack_keys[key]
                battle_system.set_attacker(user)
                steps = battle_system.activate(attack_index)  # Activates the move specified by the user input.
                if steps:
                    step_index = 0  # moves can have multiple effects; sets to the 0th index effect
                    target_index = 0  # each effect has a designated target
                old_time = time.time()
                attack_time_left = time_for_one_tile

    if user.has_turn and not motion_time_left and not attack_time_left:
        # Sprint
        if keyboard_input.is_held(pygame.K_LSHIFT):
            time_for_one_tile = constants.FASTER_TIME_FOR_ONE_TILE
        else:
            time_for_one_tile = constants.TIME_FOR_ONE_TILE

        # User Movement
        for key in constants.direction_keys:
            if keyboard_input.is_pressed(key) or keyboard_input.is_held(key):
                user.direction = constants.direction_keys[key]
                user.current_image = user.image_dict["Walk"][user.direction][0]
                if user.direction in user.possible_directions():
                    user.move_on_grid(None)
                    user.has_turn = False
                    motion = True
                break  # Only one direction need be processed
    
    # Update
    if not user.has_turn and not motion_time_left and not attack_time_left:  # Enemy Attack Phase
        for enemy in d.active_enemies:
            if enemy.has_turn:
                if 1 <= enemy.distance_to_target(user) < 2:  # If the enemy is adjacent to the user
                    enemy.move_in_direction_of_minimal_distance(user, list(direction.Direction))  # Faces user
                    enemy.current_image = enemy.image_dict["Walk"][enemy.direction][0]

                    possible_attack_indices = [i for i in range(4) if enemy.move_set.moveset[i].pp and enemy.get_targets(enemy.move_set.moveset[i].effects[0])]
                    if possible_attack_indices:
                        attack_index = random.choice(possible_attack_indices)
                    else:
                        attack_index = None
                        break
                    battle_system.set_attacker(enemy)
                    steps = battle_system.activate(attack_index)
                    if steps[0]["Targets"]:
                        step_index = 0
                        target_index = 0
                        old_time = time.time()
                        attack_time_left = time_for_one_tile
                    break
    
    if not user.has_turn and not motion_time_left and not attack_time_left:  # Enemy Movement Phase
        for enemy in [s for s in d.active_enemies if s.has_turn]:
            enemy.move_on_grid(user)  # Otherwise, just move the position of the enemy
            enemy.has_turn = False
            motion = True

    if motion:
        motion = False
        old_time = time.time()
        motion_time_left = time_for_one_tile  # Resets timer

    if motion_time_left > 0:
        t = time.time() - old_time
        old_time = time.time()
        motion_time_left = max(motion_time_left - t, 0)

        for sprite in d.all_sprites:
            sprite.motion_animation(motion_time_left, time_for_one_tile)

    elif attack_time_left > 0:
        t = time.time() - old_time
        old_time = time.time()
        attack_time_left =  max(attack_time_left - t, 0)

        if steps:
            targets = steps[step_index]["Targets"]
            target = targets[target_index]
            effect = steps[step_index]["Effect"]
            target.do_animation(effect, attack_time_left, time_for_one_tile, display)
            battle_system.attacker.attack_animation(battle_system.current_move, attack_time_left, time_for_one_tile)

        if attack_time_left == 0 and steps:
            battle_system.attacker.current_image = battle_system.attacker.image_dict["Walk"][battle_system.attacker.direction][0]
            if target_index + 1 != len(steps[step_index]["Targets"]):
                target_index += 1
                attack_time_left = time_for_one_tile
            elif step_index + 1 != len(steps):
                step_index += 1
                target_index = 0
                attack_time_left = time_for_one_tile
            else:
                steps = []
                target_index = 0
                step_index = 0
                battle_system.attacker.has_turn = False

    if motion_time_left == 0 and attack_time_left == 0:
        d.remove_dead()
        if d.user_is_dead():
            running = False
        elif d.user_at_stairs():
            d.next_floor()
        elif user.grid_pos in d.dungeon_map.trap_coords:
            pass

        if d.is_next_turn():
            d.next_turn()

    if motion_time_left == 0:
        x = constants.DISPLAY_WIDTH / 2 - user.grid_pos[0] * constants.TILE_SIZE
        y = constants.DISPLAY_HEIGHT / 2 - user.grid_pos[1] * constants.TILE_SIZE
    else:
        x = constants.DISPLAY_WIDTH / 2 - user.blit_pos[0]
        y = constants.DISPLAY_HEIGHT / 2 - user.blit_pos[1]

    # Render
    display.fill(constants.BLACK)
    display.blit(d.surface, (x, y))

    for sprite in d.all_sprites:
        sprite.draw(x, y, display)

    display.blit(d.draw_hud(), (0, 0))

    textbox.message_log.draw()
    if message_toggle:
        textbox.message_log.blit_on_display(display)

    pygame.display.update()
    clock.tick(constants.FPS)

pygame.quit()