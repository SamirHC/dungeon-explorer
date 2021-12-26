import time
from dungeon import Dungeon
from PokemonStructure import *

def draw_hud(current_floor, user):
    # FloorNo
    cool_font("Floor " + str(current_floor), RED, (0, 0))
    # Level
    cool_font("Level " + str(user.battle_info.level), RED, (display_width * (0.1), 0))
    # HP
    base_hp = user.battle_info.base["HP"]
    current_hp = user.battle_info.status["HP"]
    cool_font("HP " + str(current_hp) + " of " + str(base_hp), RED, (display_width * (0.2), 0))
    # HP BAR
    BAR_HEIGHT = display_height * 0.03
    BAR_POSITION = (display_width * (0.4), 0)
    WIDTH_SCALE = 1.5

    p.draw.rect(display, RED, (BAR_POSITION[0], BAR_POSITION[1], base_hp * WIDTH_SCALE, BAR_HEIGHT))
    if current_hp > 0:
        p.draw.rect(display, GREEN, (BAR_POSITION[0], BAR_POSITION[1], current_hp * WIDTH_SCALE, BAR_HEIGHT))
    p.draw.rect(display, BLACK, (BAR_POSITION[0], BAR_POSITION[1], base_hp * WIDTH_SCALE, 2))
    p.draw.rect(display, BLACK, (BAR_POSITION[0], BAR_POSITION[1] + BAR_HEIGHT - 2, base_hp * WIDTH_SCALE, 2))
    p.draw.rect(display, WHITE, (BAR_POSITION[0], BAR_POSITION[1], base_hp * WIDTH_SCALE, 1))
    p.draw.rect(display, WHITE, (BAR_POSITION[0], BAR_POSITION[1] + BAR_HEIGHT - 2, base_hp * WIDTH_SCALE, 1))


def remove_dead():
    for sprite in all_sprites:
        if sprite.battle_info.status["HP"] == 0:
            # print(sprite.BattleInfo.Name,"fainted!")
            msg = sprite.battle_info.name + " fainted!"
            text_box.append(Text(msg))
            all_sprites.remove(sprite)
    return not "User" not in [sprite.poke_type for sprite in all_sprites]


dungeon_id = "BeachCave"
dungeon = Dungeon(dungeon_id)

user = Pokemon("025", "User")
user.spawn(dungeon.dungeon_map)
init_hp = user.battle_info.status["HP"]
current_floor = 1

# Enemies
num_enemies = 6
for _ in range(num_enemies):
    enemy = dungeon.get_random_pokemon()
    enemy.spawn(dungeon.dungeon_map)

# MAIN LOOP###
direction = None
attack_index = None
motion = False
message_toggle = True
menu_toggle = False
time_for_one_tile = TIME_FOR_ONE_TILE
motion_time_left = 0
attack_time_left = 0
turn_count = 0
REGENRATE = 2
t = time.time()

running = True
while running:
    # DRAWING PHASE

    if attack_index is not None and motion_time_left == 0:  # Transformations to displace coordinates: DisplayOrigin->MapOrigin
        x = display_width / 2 - user.grid_pos[0] * TILE_SIZE
        y = display_height / 2 - user.grid_pos[1] * TILE_SIZE
    else:
        x = display_width / 2 - user.blit_pos[0]  #
        y = display_height / 2 - user.blit_pos[1]  #

    display.fill(BLACK)
    display.blit(dungeon.dungeon_map.surface, (x, y))
    for sprite in all_sprites:
        sprite.draw(x, y)
    draw_hud(current_floor, user)  # Draws HP bar, User level, and floor number

    text_box.draw()
    if message_toggle:
        text_box.blit_on_display()  # Draws Message Log
    dungeon_menu.draw()
    if menu_toggle:
        dungeon_menu.blit_on_display()  # Draws Menu

    # GAMEPLAY PHASE
    keys = p.key.get_pressed()

    if user.turn and not motion_time_left and not attack_time_left:  # User Attack Phase
        if attack_index is None:
            for key in attack_keys:
                if keys[key]:
                    attack_index = attack_keys[key]

        if attack_index != None:
            steps = user.activate(dungeon.dungeon_map, attack_index)  # Activates the move specified by the user input.
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
        if keys[p.K_LSHIFT]:  # Speed up game.
            time_for_one_tile = FASTER_TIME_FOR_ONE_TILE
        else:
            time_for_one_tile = TIME_FOR_ONE_TILE  # Normal Speed

        for key in direction_keys:  # Detects if movement is made
            if keys[key]:
                direction = direction_keys[key]
        if direction:  # and sets User.direction as appropriate.
            user.direction = direction
            user.current_image = user.image_dict["Motion"][user.direction][0]
        if direction in user.possible_directions(dungeon.dungeon_map):
            user.move_on_grid(dungeon.dungeon_map, None)  # Updates the position but NOT where the sprites are blit.
            user.turn = False
            motion = True
        direction = None
    #############
    if not user.turn and not motion_time_left and not attack_time_left:  # Enemy Attack Phase
        for enemy in all_sprites:
            if enemy.poke_type == "Enemy" and enemy.turn:
                chance = True  # Chance the enemy decides to check if an attack is suitable
                if 1 <= enemy.distance_to_target(user, enemy.grid_pos) < 2 or chance:  # If the enemy is adjacent to the user
                    enemy.move_in_direction_of_minimal_distance(user, dungeon.dungeon_map, list(Direction))  # Faces user
                    enemy.current_image = enemy.image_dict["Motion"][enemy.direction][0]

                    attack_index = [i for i in range(5) if
                                    enemy.battle_info.move_set[i].pp and enemy.filter_out_of_range_targets(
                                        enemy.find_possible_targets(enemy.battle_info.move_set[i].target_type[0]),
                                        enemy.battle_info.move_set[i].ranges[0],
                                        enemy.battle_info.move_set[i].cuts_corners,
                                        dungeon.dungeon_map)
                                    ]
                    if attack_index:
                        attack_index = attack_index[random.randint(0, len(attack_index) - 1)]
                    else:
                        attack_index = None
                        break
                    steps = enemy.activate(dungeon.dungeon_map, attack_index)  # Then activates a move
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
        for sprite in all_sprites:
            if sprite.poke_type == "Enemy":
                enemy = sprite
                if enemy.turn:
                    if not 1 <= enemy.distance_to_target(user, enemy.grid_pos) < 2:
                        enemy.move_on_grid(dungeon.dungeon_map, user)  # Otherwise, just move the position of the enemy
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

        for sprite in all_sprites:  # All sprites are animated.
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
            target.do_animation(effect, attack_time_left, time_for_one_tile)
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
        elif user.grid_pos == dungeon.dungeon_map.stairs_coords:
            init_hp = user.battle_info.status["HP"]
        elif user.grid_pos in dungeon.dungeon_map.trap_coords:
            pass

        new_turn = True
        for sprite in all_sprites:
            if sprite.turn:  # If a sprite still has their turn left
                new_turn = False  # Then it is not a new turn.
                break
        if new_turn:  # Once everyone has used up their turn
            turn_count += 1
            for sprite in all_sprites:
                sprite.turn = True  # it is the next turn for everyone
                if turn_count % REGENRATE == 0 and sprite.battle_info.status["Regen"] and sprite.battle_info.status[
                    "HP"] < sprite.battle_info.base["HP"]:
                    user.battle_info.status["HP"] += 1

    p.display.update()  # Update the screen
    clock.tick(FPS)
    ################################################# MISC PHASE
    for event in p.event.get():
        if (event.type == p.QUIT) or (
                event.type is p.KEYDOWN and event.key == p.K_ESCAPE):  # Escape of the red cross to exit
            p.quit()
            running = False
        if event.type is p.KEYDOWN:
            if event.key == p.K_F11:  # F11 to toggle fullscreen
                if display.get_flags() & p.FULLSCREEN:
                    p.display.set_mode((display_width, display_height))
                else:
                    p.display.set_mode((display_width, display_height), p.FULLSCREEN | p.HWSURFACE | p.DOUBLEBUF)
            elif event.key == p.K_m:
                message_toggle = not message_toggle
            elif event.key == p.K_SPACE:
                menu_toggle = not menu_toggle
