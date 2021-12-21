import math

from damage_chart import stage_dict, type_chart
from LoadImages import stats_animation_dict
from textbox import *
import configparser


all_sprites = p.sprite.Group()


class Pokemon(p.sprite.Sprite):  # poke_type {User, Teammate, Enemy, Other..}
    def __init__(self, image_dict, current_image=None, turn=True, poke_type=None, grid_pos=None, blit_pos=None,
                 direction=(0, 1), battle_info=None):
        super().__init__()
        self.image_dict = image_dict
        self.current_image = current_image
        self.turn = turn
        self.poke_type = poke_type
        self.grid_pos = grid_pos
        self.blit_pos = blit_pos
        self.direction = direction
        self.battle_info = battle_info
        for image_type in self.image_dict:
            for direction in self.image_dict[image_type]:
                for image in self.image_dict[image_type][direction]:
                    image.set_colorkey(TRANS)

    def spawn(self, map):
        valid = False
        while not valid:
            valid = True
            i = randint(0, len(sum(map.room_coords, [])) - 1)
            for s in all_sprites:
                if s.grid_pos == sum(map.room_coords, [])[i]:
                    valid = False  # If a pokemon already occupies that space

        self.grid_pos = sum(map.room_coords, [])[i]
        self.blit_pos = [self.grid_pos[0] * TILE_SIZE, self.grid_pos[1] * TILE_SIZE]
        all_sprites.add(self)

    def move_on_grid(self, map, target):
        possible_directions = self.possible_directions(map)
        self.move_in_direction_of_minimal_distance(target, map, possible_directions)

        x = self.grid_pos[0] + self.direction[0]
        y = self.grid_pos[1] + self.direction[1]
        if self.direction in possible_directions:
            self.grid_pos = [x, y]

    def remove_corner_cutting_directions(self, possible_directions, map):
        x, y = self.grid_pos[0], self.grid_pos[1]
        for i in [(-1, 0), (0, -1), (1, 0), (0, 1)]:
            x_dir, y_dir = i[0], i[1]

            if map.floor[y + y_dir][x + x_dir] == " ":  # Prevents cutting corners when walls exist.
                if x_dir:
                    for k in range(len(possible_directions) - 1, -1, -1):
                        if x_dir == possible_directions[k][0]:
                            del possible_directions[k]
                elif y_dir:
                    for k in range(len(possible_directions) - 1, -1, -1):
                        if y_dir == possible_directions[k][1]:
                            del possible_directions[k]
        return possible_directions

    def remove_tile_directions(self, possible_directions, map, tile):
        x, y = self.grid_pos[0], self.grid_pos[1]
        for i in range(len(possible_directions) - 1, -1, -1):  # Prevents walking through non-ground tiles and through other pokemon.
            xdir, ydir = possible_directions[i][0], possible_directions[i][1]
            if map.floor[y + ydir][x + xdir] == tile:
                del possible_directions[i]
        return possible_directions

    def possible_directions(self, map):  # lists the possible directions the pokemon may MOVE in.
        possible_directions = [(i, j) for i in range(-1, 2) for j in range(-1, 2)]
        if self.battle_info.type1 != "Ghost" and self.battle_info.type2 != "Ghost":
            possible_directions = self.remove_corner_cutting_directions(possible_directions, map)
            possible_directions = self.remove_tile_directions(possible_directions, map, " ")
        if self.battle_info.type1 != "Water" and self.battle_info.type2 != "Water":
            possible_directions = self.remove_tile_directions(possible_directions, map, "F")

        for sprite in all_sprites:
            if 1 <= self.distance_to_target(sprite, self.grid_pos) < 2:
                if self.vector_to_target(sprite, self.grid_pos) in possible_directions:
                    possible_directions.remove(self.vector_to_target(sprite, self.grid_pos))

        return possible_directions  # Lists directions unoccupied and non-wall tiles(that aren't corner obstructed)

    def draw(self, x, y):
        a = self.blit_pos[0] + x
        b = self.blit_pos[1] + y
        scaled_shift = (POKE_SIZE - TILE_SIZE) // 2
        if self.poke_type in ["User", "Team"]:
            p.draw.ellipse(display, (255, 247, 0), (
                a + TILE_SIZE * 4 / 24, b + TILE_SIZE * 16 / 24, TILE_SIZE * 16 / 24, TILE_SIZE * 8 / 24))  # Yellow edge
            p.draw.ellipse(display, (222, 181, 0), (
                a + TILE_SIZE * 5 / 24, b + TILE_SIZE * 17 / 24, TILE_SIZE * 14 / 24,
                TILE_SIZE * 6 / 24))  # Lightbrown fade
            p.draw.ellipse(display, (165, 107, 0), (
                a + TILE_SIZE * 6 / 24, b + TILE_SIZE * 17 / 24, TILE_SIZE * 12 / 24, TILE_SIZE * 6 / 24))  # Brown ellipse
        else:
            p.draw.ellipse(display, BLACK, (
                a + TILE_SIZE * 4 / 24, b + TILE_SIZE * 16 / 24, TILE_SIZE * 16 / 24, TILE_SIZE * 8 / 24))  # BlackShadow

        display.blit(self.current_image, (a - scaled_shift, b - scaled_shift))  # The pokemon image files are 200x200 px while tiles are 60x60. (200-60)/2 = 70 <- Centred when shifted by 70.

    ##############
    def vector_to_target(self, target, position):
        return (target.grid_pos[0] - position[0], target.grid_pos[1] - position[1])

    def distance_to_target(self, target, position):
        vector = self.vector_to_target(target, position)
        return (vector[0] ** 2 + vector[1] ** 2) ** (0.5)

    def check_aggro(self, target, map):
        distance, vector = self.distance_to_target(target, self.grid_pos), self.vector_to_target(target, self.grid_pos)
        for room in map.room_coords:
            if self.grid_pos in room and target.grid_pos in room:  # Pokemon aggro onto the user if in the same room
                same_room = True
                break
            else:
                same_room = False

        if distance <= AGGRO_RANGE or same_room:  # Pokemon also aggro if withing a certain range AGGRORANGE
            return distance, vector, True
        else:
            return None, None, False

    def move_in_direction_of_minimal_distance(self, target, map, possible_directions):
        if not target:
            return
        elif target.grid_pos == (self.grid_pos[0] + self.direction[0], self.grid_pos[1] + self.direction[1]):
            return  # Already facing target, no need to change direction

        distance, vector, aggro = self.check_aggro(target, map)
        if aggro:
            if distance < 2:
                self.direction = vector
                return

            new_pos = self.grid_pos
            new_direction = self.direction

            for direction in possible_directions:
                surrounding_pos = (self.grid_pos[0] + direction[0], self.grid_pos[1] + direction[1])
                new_distance = self.distance_to_target(target, surrounding_pos)

                if new_distance < distance:
                    distance = new_distance
                    new_direction = direction

            self.direction = new_direction

        else:  # Face a random, but valid direction if not aggro
            i = randint(0, len(possible_directions) - 1)
            self.direction = possible_directions[i]

    ################
    # ANIMATIONS
    def motion_animation(self, motion_time_left, time_for_one_tile):
        if self.blit_pos != [self.grid_pos[0] * TILE_SIZE, self.grid_pos[1] * TILE_SIZE]:
            images = self.image_dict["Motion"][self.direction]
            step_size = 1 / len(images)
            for i in range(len(images)):
                if step_size * i <= motion_time_left / time_for_one_tile < step_size * (i + 1):
                    self.current_image = self.image_dict["Motion"][self.direction][(i + 2) % len(images)]

            self.blit_pos[0] = (self.grid_pos[0] - (self.direction[0] * motion_time_left / time_for_one_tile)) * TILE_SIZE
            self.blit_pos[1] = (self.grid_pos[1] - (self.direction[1] * motion_time_left / time_for_one_tile)) * TILE_SIZE
            if self.blit_pos[0] == self.grid_pos[0] * TILE_SIZE and self.blit_pos[1] == self.grid_pos[1] * TILE_SIZE:
                self.current_image = self.image_dict["Motion"][self.direction][0]

    def do_animation(self, effect, attack_time_left, time_for_one_tile):
        if effect == "Damage":
            self.hurt_animation(attack_time_left, time_for_one_tile)
        elif effect in ["ATK+", "ATK-", "DEF+", "DEF-", "SPATK+", "SPATK-", "SPDEF+", "SPDEF-"]:
            self.stat_animation(effect, attack_time_left, time_for_one_tile)
        elif effect in []:
            self.afflict_animation()
        else:
            pass

    def afflict_animation(self):
        pass

    def hurt_animation(self, attack_time_left, time_for_one_tile):
        if self.battle_info.status["HP"] == 0:
            upper_bound = 1.5
        else:
            upper_bound = 0.85
        if 0.15 < attack_time_left / time_for_one_tile <= upper_bound:
            self.current_image = self.image_dict["Hurt"][self.direction][0]
        else:
            self.current_image = self.image_dict["Motion"][self.direction][0]

    def attack_animation(self, attack_index, attack_time_left, time_for_one_tile):
        category = self.battle_info.move_set[attack_index].category
        if category == "Physical" or category == "Special":
            pass
        elif category == "Status":
            category = "Special"
        else:
            return

        images = self.image_dict[category][self.direction]
        step_size = 1 / len(images)
        for i in range(len(images)):
            if step_size * i <= attack_time_left / time_for_one_tile < step_size * (i + 1):
                self.current_image = self.image_dict[category][self.direction][i]

        if category == "Physical":
            self.blit_pos[0] = (self.grid_pos[0] + (self.direction[0]) * 2 * (
                    0.25 - (0.5 - (attack_time_left / time_for_one_tile)) ** 2)) * TILE_SIZE
            self.blit_pos[1] = (self.grid_pos[1] + (self.direction[1]) * 2 * (
                    0.25 - (0.5 - (attack_time_left / time_for_one_tile)) ** 2)) * TILE_SIZE

    def stat_animation(self, effect, attack_time_left, time_for_one_tile):
        stat = effect[:-1]
        action = effect[-1]
        images = stats_animation_dict[stat][action]
        step_size = 1 / len(images)
        for sprite in all_sprites:
            if sprite.poke_type == "User":
                x = self.blit_pos[0] + display_width / 2 - sprite.blit_pos[0]
                y = self.blit_pos[1] + display_height / 2 - sprite.blit_pos[1]
                break
        for i in range(len(images)):
            if step_size * i <= attack_time_left / time_for_one_tile < step_size * (i + 1):
                display.blit(images[i], (x, y))
                break

    ################
    def miss(self, move_accuracy, evasion):
        i = randint(0, 99)
        raw_accuracy = self.battle_info.status["ACC"] / 100 * move_accuracy
        if round(raw_accuracy - evasion) > i:
            return False
        else:
            return True

    def activate(self, map, move_index):
        if move_index == None:
            return []
        move_used = self.battle_info.move_set[move_index]
        steps = []
        if move_used.pp != 0:
            move_used.pp -= 1

            msg = self.battle_info.name + " used " + move_used.name
            message_log.write(Text(msg).draw_text())

            for i in range(len(move_used.effects)):
                Dict = {}
                effect = move_used.effects[i]
                move_range = move_used.ranges[i]
                target_type = move_used.target_type[i]
                targets = self.find_possible_targets(target_type)
                targets = self.filter_out_of_range_targets(targets, move_range, move_used.cuts_corners, map)
                if targets:
                    Dict["Targets"] = targets
                    Dict["Effect"] = effect
                    steps.append(Dict)
                    self.activate_effect(move_used, i, targets)
                else:
                    if i == 0:
                        msg = "The move failed."
                        message_log.write(Text(msg).draw_text())
                    break
        else:
            msg = "You have ran out of PP for this move."
            message_log.write(Text(msg).draw_text())

        return steps

    def activate_effect(self, move, index, targets):
        effect = move.effects[index]
        if effect == "Damage":
            for target in targets:

                evasion = target.battle_info.status["EVA"]
                if target == self:  # You cannot dodge recoil damage
                    evasion = 0

                if self.miss(move.accuracy[index], evasion):
                    msg = self.battle_info.name + " missed."
                else:
                    damage = self.battle_info.deal_damage(move, target, index)
                    target.battle_info.lose_hp(damage)
                    if target != self:
                        msg = target.battle_info.name + " took " + str(damage) + " damage!"
                    else:
                        msg = target.battle_info.name + " took " + str(damage) + " recoil damage!"
                message_log.write(Text(msg).draw_text())
                print(self.battle_info.name, self.battle_info.status["HP"])
                print(target.battle_info.name, target.battle_info.status["HP"])

        elif effect == "FixedDamage":
            for target in targets:
                target.battle_info.lose_hp(move.power[index])

        elif effect == "Heal":
            for target in targets:
                target.battle_info.heal(move.power[index])

        elif effect in ("ATK+", "ATK-", "DEF+", "DEF-", "SPATK+", "SPATK-", "SPDEF+", "SPDEF-", "ACC+", "ACC-", "EVA+", "EVA-"):
            for target in targets:
                evasion = target.battle_info.status["EVA"]
                if target == self:  # You cannot dodge recoil damage
                    evasion = 0
                if self.miss(move.accuracy[index], evasion):
                    msg = self.battle_info.name + " missed."
                else:
                    target.battle_info.stat_change(effect, move.power[index])

        elif effect in ("Poisoned", "Badly Poisoned", "Burned", "Frozen", "Paralyzed", "Sleeping", "Constricted", "Paused"):
            for target in targets:
                evasion = target.battle_info.status["EVA"]
                if target == self:  # You cannot dodge recoil damage
                    evasion = 0
                if index == 0:
                    if self.miss(move.accuracy[index], evasion):
                        msg = self.battle_info.name + " missed."
                    else:
                        target.battle_info.afflict(effect, move.power[index])
                        msg = target.battle_info.name + " is now " + effect
                    message_log.write(Text(msg).draw_text())

    def find_possible_targets(self, target_type):
        allies = [sprite for sprite in all_sprites if sprite.poke_type in ("User", "Team")]
        enemies = [sprite for sprite in all_sprites if sprite.poke_type == "Enemy"]
        if self.poke_type == "Enemy":
            allies, enemies = enemies, allies

        if target_type == "Self":
            return [self]
        elif target_type == "All":
            return [sprite for sprite in all_sprites]
        elif target_type == "Allies":
            return allies
        elif target_type == "Enemies":
            return enemies
        elif target_type == "Non-Self":
            return [sprite for sprite in all_sprites if sprite != self]

    def filter_out_of_range_targets(self, targets, move_range, cuts_corners, map):
        if move_range == "0":
            return [self]

        possible_directions = [(i, j) for i in range(-1, 2) for j in range(-1, 2)]
        if not cuts_corners:
            possible_directions = self.remove_corner_cutting_directions(possible_directions, map)

        if move_range == "1" or move_range == "2" or move_range == "10":  # Front
            possible_directions = self.remove_tile_directions(possible_directions, map, " ")
            if self.direction in possible_directions:
                for n in range(1, int(move_range) + 1):
                    for target in targets:
                        x = self.grid_pos[0] + n * self.direction[0]
                        y = self.grid_pos[1] + n * self.direction[1]
                        if map.floor[y][x] == " ":
                            return []
                        if (target.grid_pos[0] == x) and (target.grid_pos[1] == y):
                            return [target]

        if move_range == "S" or move_range == "R":  # Surrounding
            new_targets = []
            for target in targets:
                for direction in possible_directions:
                    x = self.grid_pos[0] + direction[0]
                    y = self.grid_pos[1] + direction[1]
                    if (target.grid_pos[0] == x) and (target.grid_pos[1] == y):
                        new_targets.append(target)
            if move_range == "S":
                return new_targets
            else:  # Range == "R"
                x = self.grid_pos[0]
                y = self.grid_pos[1]

                if map.floor[y][x] == "R":
                    for room in map.room_coords:
                        if [x, y] in room:
                            possible_directions = room
                            break
                    for target in targets:
                        if target.grid_pos in possible_directions:
                            new_targets.append(target)
                new_targets = remove_duplicates(new_targets)
                return new_targets
        return []


###################################################################################################
# Moves
def load_move_data():
    move_dict = {}
    directory = os.path.join(os.getcwd(), "GameData", "Moves")
    config = configparser.RawConfigParser()
    for move in os.listdir(directory):
        temp_dict = {}
        move_dir = os.path.join(directory, move, "moveData.cfg")
        config.read(move_dir)
        section = config.sections()[0]
        options = config.options(section)
        for option in options:
            temp_dict[option] = config.get(section, option)
        move_dict[move] = temp_dict
    return move_dict

move_dict = load_move_data()

class Move:
    def __init__(self, name):
        self.name = name
        # Single
        self.power = [int(x) for x in move_dict[name]["power"].split(",")]
        self.accuracy = [int(x) for x in move_dict[name]["accuracy"].split(",")]
        self.critical = int(move_dict[name]["critical"])
        self.pp = int(move_dict[name]["pp"])
        self.type = move_dict[name]["type"]
        self.category = move_dict[name]["category"]  # ["ATK","SPATK"]
        self.cuts_corners = int(move_dict[name]["cutscorners"])  # 1/0 [True/False]
        # Multi
        self.target_type = move_dict[name]["targettype"].split(",")  # ["Self","Allies","Enemies","All"]
        self.ranges = move_dict[name]["ranges"].split(",")
        self.effects = move_dict[name]["effects"].split(",")  # ["Damage","Heal","ATK+","DEF+","SPATK+","SPDEF+","ATK-","DEF-","SPATK-","SPDEF-"...]

    def empty_pp(self):
        self.pp = 0


class PokemonBattleInfo:
    def __init__(self, poke_id, name, level, xp, type1, type2, base, status, move_set):
        self.poke_id = poke_id
        self.name = name
        self.level = level
        self.xp = xp
        self.type1 = type1
        self.type2 = type2
        self.base = base
        self.status = status
        self.move_set = move_set

    def lose_hp(self, amount):
        self.status["HP"] -= amount
        if self.status["HP"] < 0:
            self.status["HP"] = 0

    def deal_damage(self, move, target, index):
        # Step 0 - Determine Stats
        if move.category == "Physical":
            A = self.base["ATK"] * stage_dict[self.status["ATK"]]
            D = target.battle_info.base["DEF"] * stage_dict[target.battle_info.status["DEF"]]
        elif move.category == "Special":
            A = self.base["SPATK"] * stage_dict[self.status["SPATK"]]
            D = target.battle_info.base["SPDEF"] * stage_dict[target.battle_info.status["SPDEF"]]
        else:
            return 0
        L = self.level
        P = move.power[index]
        if target.poke_type in ["User", "Team"]:
            Y = 340 / 256
        else:
            Y = 1
        log_input = ((A - D) / 8 + L + 50) * 10
        if log_input < 1:
            log_input = 1
        elif log_input > 4095:
            log_input = 4095
        critical_chance = randint(0, 99)

        # Step 1 - Stat Modification
        # Step 2 - Raw Damage Calculation
        damage = ((A + P) * (39168 / 65536) - (D / 2) + 50 * math.log(log_input) - 311) / Y
        # Step 3 - Final Damage Modifications
        if damage < 1:
            damage = 1
        elif damage > 999:
            damage = 999

        damage *= type_chart.get_multiplier(move.type, target.battle_info.type1) * type_chart.get_multiplier(move.type, target.battle_info.type2)  # Apply type advantage multiplier
        if move.critical > critical_chance:
            damage *= 1.5
        # Step 4 - Final Calculations
        damage *= (randint(0, 16383) + 57344) / 65536  # Random pertebation
        damage = round(damage)

        return damage

    def stat_change(self, effect, power):
        if effect[-1] == "+":
            effect = effect[:-1]
            self.status[effect] += power
            if self.status[effect] > 20:
                self.status[effect] = 20

        elif effect[-1] == "-":
            effect = effect[:-1]
            self.status[effect] -= power
            if self.status[effect] < 0:
                self.status[effect] = 0

    def afflict(self, effect, power):

        if not self.status[effect]:
            self.status[effect] = power
        else:
            print(self.name, "is already", effect)

    def heal(self, power):
        self.status["HP"] += power
