import battlesystem
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
import textbox
import utils

# Draws HP bar, User level, and floor number
def draw_hud(current_floor: int, user: pokemon.Pokemon):
    # FloorNo
    utils.cool_font("Floor " + str(current_floor), constants.RED, (0, 0), display)
    # Level
    utils.cool_font("Level " + str(user.battle_info.base.level), constants.RED, (constants.DISPLAY_WIDTH * (0.1), 0), display)
    # HP
    base_hp = user.battle_info.base.hp
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

# Initialisation
pygame.init()
display = pygame.display.set_mode((constants.DISPLAY_WIDTH, constants.DISPLAY_HEIGHT))
pygame.display.set_caption(constants.CAPTION)
clock = pygame.time.Clock()

dungeon_id = "BeachCave"
user_id = "0025"
d = dungeon.Dungeon(dungeon_id)

user = pokemon.Pokemon(user_id, "User", d)
d.spawn(user)
init_hp = user.battle_info.status["HP"]

attack_index = None
motion = False
message_toggle = True
time_for_one_tile = constants.TIME_FOR_ONE_TILE
motion_time_left = 0
attack_time_left = 0
t = time.time()

battle_system = battlesystem.BattleSystem()

# Game loop
running = True
while running:
    # Render
    if attack_index is not None and motion_time_left == 0:
        x = constants.DISPLAY_WIDTH / 2 - user.grid_pos[0] * constants.TILE_SIZE
        y = constants.DISPLAY_HEIGHT / 2 - user.grid_pos[1] * constants.TILE_SIZE
    else:
        x = constants.DISPLAY_WIDTH / 2 - user.blit_pos[0]
        y = constants.DISPLAY_HEIGHT / 2 - user.blit_pos[1]

    display.fill(constants.BLACK)
    display.blit(d.surface, (x, y))

    for sprite in d.all_sprites:
        sprite.draw(x, y, display)

    draw_hud(d.floor_number, user)

    textbox.message_log.draw()
    if message_toggle:
        textbox.message_log.blit_on_display(display)

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
            elif event.key in constants.attack_keys:
                if user.has_turn and not motion_time_left and not attack_time_left:
                    attack_index = constants.attack_keys[event.key]

    if user.has_turn and not motion_time_left and not attack_time_left:  # User Attack Phase
        if attack_index != None:
            battle_system.set_attacker(user)
            steps = battle_system.activate(attack_index)  # Activates the move specified by the user input.
            if steps:
                step_index = 0  # moves can have multiple effects; sets to the 0th index effect
                target_index = 0  # each effect has a designated target
            else:
                attack_index = None
            old_time = time.time()
            attack_time_left = time_for_one_tile

    if user.has_turn and not motion_time_left and not attack_time_left:  # User Movement Phase
        if pressed[pygame.K_LSHIFT]:
            time_for_one_tile = constants.FASTER_TIME_FOR_ONE_TILE
        else:
            time_for_one_tile = constants.TIME_FOR_ONE_TILE

        for key in constants.direction_keys:
            if pressed[key]:
                user.direction = constants.direction_keys[key]
                user.current_image = user.image_dict["Walk"][user.direction][0]
                if user.direction in user.possible_directions():
                    user.move_on_grid(None)
                    user.has_turn = False
                    motion = True
                break  # Only one direction need be processed
    
    if not user.has_turn and not motion_time_left and not attack_time_left:  # Enemy Attack Phase
        for enemy in d.all_sprites:
            if enemy.poke_type == "Enemy" and enemy.has_turn:
                if 1 <= enemy.distance_to_target(user) < 2:  # If the enemy is adjacent to the user
                    enemy.move_in_direction_of_minimal_distance(user, list(direction.Direction))  # Faces user
                    enemy.current_image = enemy.image_dict["Walk"][enemy.direction][0]

                    attack_index = [i for i in range(4) if
                                    enemy.battle_info.move_set.moveset[i].pp and enemy.filter_out_of_range_targets(
                                        enemy.find_possible_targets(enemy.battle_info.move_set.moveset[i].target_type[0]),
                                        enemy.battle_info.move_set.moveset[i].ranges[0],
                                        enemy.battle_info.move_set.moveset[i].cuts_corners)
                                    ]
                    if attack_index:
                        attack_index = random.choice(attack_index)
                    else:
                        attack_index = None
                        break
                    battle_system.set_attacker(enemy)
                    steps = battle_system.activate(attack_index)
                    if steps:
                        step_index = 0
                        target_index = 0
                    else:
                        attack_index = None
                    old_time = time.time()
                    attack_time_left = time_for_one_tile
                    break
    
    if not user.has_turn and not motion_time_left and not attack_time_left:  # Enemy Movement Phase
        for enemy in [s for s in d.all_sprites if s.poke_type == "Enemy" and s.has_turn]:
            if not 1 <= enemy.distance_to_target(user) < 2:
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
            battle_system.attacker.attack_animation(attack_index, attack_time_left, time_for_one_tile)

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
                attack_index = None
                battle_system.attacker.has_turn = False

    if motion_time_left == 0 and attack_time_left == 0:
        d.remove_dead()
        if d.user_is_dead():
            running = False
        elif user.grid_pos == d.dungeon_map.stairs_coords:
            init_hp = user.battle_info.status["HP"]
        elif user.grid_pos in d.dungeon_map.trap_coords:
            pass

        new_turn = d.is_next_turn()
        if new_turn:
            d.next_turn()

    pygame.display.update()
    clock.tick(constants.FPS)

pygame.quit()