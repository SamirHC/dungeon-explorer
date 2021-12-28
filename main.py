import constants
import direction
import dungeon
import pokemon
import pygame
import pygame.display
import pygame.draw
import pygame.event
import pygame.key
import pygame.time
import random
import time
import text
import textbox
import utils

def draw_hud(current_floor: int, user: pokemon.Pokemon):
    # FloorNo
    utils.cool_font("Floor " + str(current_floor), constants.RED, (0, 0), display)
    # Level
    utils.cool_font("Level " + str(user.battle_info.level), constants.RED, (constants.DISPLAY_WIDTH * (0.1), 0), display)
    # HP
    base_hp = user.battle_info.base["HP"]
    current_hp = user.battle_info.status["HP"]
    utils.cool_font("HP " + str(current_hp) + " of " + str(base_hp), constants.RED, (constants.DISPLAY_WIDTH * (0.2), 0), display)
    # HP BAR
    BAR_HEIGHT = constants.DISPLAY_HEIGHT * 0.03
    BAR_POSITION = (constants.DISPLAY_WIDTH * (0.4), 0)
    WIDTH_SCALE = 1.5

    pygame.draw.rect(display, constants.RED, (BAR_POSITION[0], BAR_POSITION[1], base_hp * WIDTH_SCALE, BAR_HEIGHT))
    if current_hp > 0:
        pygame.draw.rect(display, constants.GREEN, (BAR_POSITION[0], BAR_POSITION[1], current_hp * WIDTH_SCALE, BAR_HEIGHT))
    pygame.draw.rect(display, constants.BLACK, (BAR_POSITION[0], BAR_POSITION[1], base_hp * WIDTH_SCALE, 2))
    pygame.draw.rect(display, constants.BLACK, (BAR_POSITION[0], BAR_POSITION[1] + BAR_HEIGHT - 2, base_hp * WIDTH_SCALE, 2))
    pygame.draw.rect(display, constants.WHITE, (BAR_POSITION[0], BAR_POSITION[1], base_hp * WIDTH_SCALE, 1))
    pygame.draw.rect(display, constants.WHITE, (BAR_POSITION[0], BAR_POSITION[1] + BAR_HEIGHT - 2, base_hp * WIDTH_SCALE, 1))


def remove_dead():
    for sprite in pokemon.all_sprites:
        if sprite.battle_info.status["HP"] == 0:
            # print(sprite.BattleInfo.Name,"fainted!")
            msg = sprite.battle_info.name + " fainted!"
            textbox.text_box.append(text.Text(msg))
            pokemon.all_sprites.remove(sprite)
    return not "User" not in [sprite.poke_type for sprite in pokemon.all_sprites]

pygame.init()

display = pygame.display.set_mode((constants.DISPLAY_WIDTH, constants.DISPLAY_HEIGHT))
pygame.display.set_caption(constants.CAPTION)
clock = pygame.time.Clock()

dungeon_id = "BeachCave"
d = dungeon.Dungeon(dungeon_id)

user = pokemon.Pokemon("025", "User", d)
user.spawn()
init_hp = user.battle_info.status["HP"]

# Enemies
num_enemies = 6
for _ in range(num_enemies):
    enemy = d.get_random_pokemon()
    enemy.spawn()

# MAIN LOOP###
attack_index = None
motion = False
message_toggle = True
menu_toggle = False
time_for_one_tile = constants.TIME_FOR_ONE_TILE
motion_time_left = 0
attack_time_left = 0
REGENRATE = 2
t = time.time()

running = True
while running:
    # DRAWING PHASE

    if attack_index is not None and motion_time_left == 0:  # Transformations to displace coordinates: DisplayOrigin->MapOrigin
        x = constants.DISPLAY_WIDTH / 2 - user.grid_pos[0] * constants.TILE_SIZE
        y = constants.DISPLAY_HEIGHT / 2 - user.grid_pos[1] * constants.TILE_SIZE
    else:
        x = constants.DISPLAY_WIDTH / 2 - user.blit_pos[0]  #
        y = constants.DISPLAY_HEIGHT / 2 - user.blit_pos[1]  #

    display.fill(constants.BLACK)
    display.blit(d.dungeon_map.surface, (x, y))
    for sprite in pokemon.all_sprites:
        sprite.draw(x, y, display)
    draw_hud(d.floor_number, user)  # Draws HP bar, User level, and floor number

    textbox.text_box.draw()
    if message_toggle:
        textbox.text_box.blit_on_display(display)  # Draws Message Log
    textbox.dungeon_menu.draw()
    if menu_toggle:
        textbox.dungeon_menu.blit_on_display(display)  # Draws Menu

    # Input
    pressed = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                if display.get_flags() & pygame.FULLSCREEN:
                    pygame.display.set_mode((constants.DISPLAY_WIDTH, constants.DISPLAY_HEIGHT))
                else:
                    pygame.display.set_mode((constants.DISPLAY_WIDTH, constants.DISPLAY_HEIGHT), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
            elif event.key == pygame.K_m:
                message_toggle = not message_toggle
            elif event.key == pygame.K_SPACE:
                menu_toggle = not menu_toggle

    if user.turn and not motion_time_left and not attack_time_left:  # User Attack Phase
        if attack_index is None:
            for key in constants.attack_keys:
                if pressed[key]:
                    attack_index = constants.attack_keys[key]

        if attack_index != None:
            steps = user.activate(attack_index)  # Activates the move specified by the user input.
            if steps:
                step_index = 0  # moves can have multiple effects; sets to the 0th index effect
                target_index = 0  # each effect has a designated target
                attacker = user
            else:
                attack_index = None
            old_time = time.time()
            attack_time_left = time_for_one_tile  # Resets timer

    #################
    if user.turn and not motion_time_left and not attack_time_left:  # User Movement Phase
        if pressed[pygame.K_LSHIFT]:  # Speed up game.
            time_for_one_tile = constants.FASTER_TIME_FOR_ONE_TILE
        else:
            time_for_one_tile = constants.TIME_FOR_ONE_TILE  # Normal Speed

        for key in constants.direction_keys:
            if pressed[key]:
                user.direction = constants.direction_keys[key]
                user.current_image = user.image_dict["Motion"][user.direction][0]
                if user.direction in user.possible_directions():
                    user.move_on_grid(None)
                    user.turn = False
                    motion = True
                break  # Only one direction need be processed
    #############
    if not user.turn and not motion_time_left and not attack_time_left:  # Enemy Attack Phase
        for enemy in pokemon.all_sprites:
            if enemy.poke_type == "Enemy" and enemy.turn:
                chance = True  # Chance the enemy decides to check if an attack is suitable
                if 1 <= enemy.distance_to_target(user) < 2 or chance:  # If the enemy is adjacent to the user
                    enemy.move_in_direction_of_minimal_distance(user, list(direction.Direction))  # Faces user
                    enemy.current_image = enemy.image_dict["Motion"][enemy.direction][0]

                    attack_index = [i for i in range(5) if
                                    enemy.battle_info.move_set[i].pp and enemy.filter_out_of_range_targets(
                                        enemy.find_possible_targets(enemy.battle_info.move_set[i].target_type[0]),
                                        enemy.battle_info.move_set[i].ranges[0],
                                        enemy.battle_info.move_set[i].cuts_corners)
                                    ]
                    if attack_index:
                        attack_index = attack_index[random.randint(0, len(attack_index) - 1)]
                    else:
                        attack_index = None
                        break
                    steps = enemy.activate(attack_index)  # Then activates a move
                    if steps:
                        step_index = 0
                        target_index = 0
                        attacker = enemy
                    else:
                        attack_index = None
                    old_time = time.time()
                    attack_time_left = time_for_one_tile  # Resets timer
                    break
    ##############
    if not user.turn and not motion_time_left and not attack_time_left:  # Enemy Movement Phase
        for sprite in pokemon.all_sprites:
            if sprite.poke_type == "Enemy":
                enemy = sprite
                if enemy.turn:
                    if not 1 <= enemy.distance_to_target(user) < 2:
                        enemy.move_on_grid(user)  # Otherwise, just move the position of the enemy
                        enemy.turn = False
                        motion = True

    #############
    if motion:
        motion = False
        old_time = time.time()
        motion_time_left = time_for_one_tile  # Resets timer

    ##################################### ANIMATION PHASE
    if motion_time_left > 0:
        t = time.time() - old_time
        old_time = time.time()
        motion_time_left -= t  # reduce time left by change in time.
        if motion_time_left <= 0:
            motion_time_left = 0  # Time is up.

        for sprite in pokemon.all_sprites:  # All sprites are animated.
            sprite.motion_animation(motion_time_left, time_for_one_tile)

    elif attack_time_left > 0:
        t = time.time() - old_time
        old_time = time.time()
        attack_time_left -= t  # reduce time left by change in time.
        if attack_time_left <= 0:
            attack_time_left = 0  # Time is up.

        if steps:
            targets = steps[step_index]["Targets"]
            target = targets[target_index]
            effect = steps[step_index]["Effect"]
            target.do_animation(effect, attack_time_left, time_for_one_tile, display)
            attacker.attack_animation(attack_index, attack_time_left, time_for_one_tile)

        if attack_time_left == 0 and steps:
            attacker.current_image = attacker.image_dict["Motion"][attacker.direction][0]
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
                attack_index = None
                attacker.turn = False

    ############################################## END PHASE
    if motion_time_left == 0 and attack_time_left == 0:
        if not remove_dead():
            running = False
        elif user.grid_pos == d.dungeon_map.stairs_coords:
            init_hp = user.battle_info.status["HP"]
        elif user.grid_pos in d.dungeon_map.trap_coords:
            pass

        new_turn = True
        for sprite in pokemon.all_sprites:
            if sprite.turn:  # If a sprite still has their turn left
                new_turn = False  # Then it is not a new turn.
                break
        if new_turn:  # Once everyone has used up their turn
            d.next_turn()
            for sprite in pokemon.all_sprites:
                sprite.turn = True  # it is the next turn for everyone
                if d.turns % REGENRATE == 0 and sprite.battle_info.status["Regen"] and sprite.battle_info.status[
                    "HP"] < sprite.battle_info.base["HP"]:
                    user.battle_info.status["HP"] += 1

    pygame.display.update()
    clock.tick(constants.FPS)

pygame.quit()