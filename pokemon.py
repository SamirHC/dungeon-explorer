import constants
import direction
import LoadImages
import move
import os
import pokemon_battle_info
import pygame.draw
import pygame.image
import pygame.sprite
import pygame.transform
import random
import tile
import text
import textbox
import utils


all_sprites = pygame.sprite.Group()

class Pokemon(pygame.sprite.Sprite):  # poke_type {User, Teammate, Enemy, Other..}
    REGENRATION_RATE = 2

    def __init__(self, poke_id: str, poke_type: str, dungeon):
        super().__init__()
        self.poke_id = poke_id
        self.poke_type = poke_type
        self.dungeon = dungeon
        self.image_dict = self.pokemon_image_dict()
        self.load_pokemon_object()
        self.direction = direction.Direction.SOUTH
        self.has_turn = True
        for image_type in self.image_dict:
            for dir in self.image_dict[image_type]:
                for image in self.image_dict[image_type][dir]:
                    image.set_colorkey(constants.TRANS)
        self.current_image = self.image_dict["Motion"][self.direction][0]

    def load_pokemon_object(self):
        if self.poke_type in ("User", "Team"):
            specific_pokemon_data = self.load_user_specific_pokemon_data()
        elif self.poke_type == "Enemy":
            specific_pokemon_data = self.dungeon.foes[self.poke_id]

        base_dict = self.load_base_pokemon_data()

        level = specific_pokemon_data["LVL"]
        xp = specific_pokemon_data["XP"]
        hp = base_dict["HP"] + specific_pokemon_data["HP"]
        ATK = base_dict["ATK"] + specific_pokemon_data["ATK"]
        DEF = base_dict["DEF"] + specific_pokemon_data["DEF"]
        SPATK = base_dict["SPATK"] + specific_pokemon_data["SPATK"]
        SPDEF = base_dict["SPDEF"] + specific_pokemon_data["SPDEF"]
        move_set = []
        for i in range(1, 6):
            current_move = specific_pokemon_data["Move" + str(i)]
            move_set.append(move.Move(current_move))
        base = {
            "HP": hp,
            "ATK": ATK,
            "DEF": DEF,
            "SPATK": SPATK,
            "SPDEF": SPDEF,
            "ACC": 100,
            "EVA": 0,
            "Regen": True,
            "Belly": 100,
            "Poison": False,
            "Badly Poison": False,
            "Burn": False,
            "Frozen": False,
            "Paralyzed": False,
            "Sleeping": False,
            "Constricted": False,
            "Paused": False
        }
        status_dict = {
            "HP": hp,
            "ATK": 10,
            "DEF": 10,
            "SPATK": 10,
            "SPDEF": 10,
            "ACC": 100,
            "EVA": 0,
            "Regen": 1,
            "Belly": 100,
            "Poisoned": 0,
            "Badly Poisoned": 0,
            "Burned": 0,
            "Frozen": 0,
            "Paralyzed": 0,
            "Immobilized": 0,
            "Sleeping": 0,
            "Constricted": 0,
            "Cringed": 0,
            "Paused": 0
        }

        self.battle_info = pokemon_battle_info.PokemonBattleInfo(
            self.poke_id,
            name=base_dict["Name"],
            level=level,
            xp=xp,
            type1=base_dict["Type1"],
            type2=base_dict["Type2"],
            base=base,
            status=status_dict,
            move_set=move_set
        )

    def load_user_specific_pokemon_data(self):
        file = os.path.join(os.getcwd(), "UserData", "UserTeamData.txt")
        f = Pokemon.load_pokemon_data_file(file)
        for line in f:
            if self.poke_id == line[0]:
                return Pokemon.parse_pokemon_data_file_line(line)

    def load_pokemon_data_file(file):
        with open(file) as f:
            f = [line[:-1].split(",") for line in f.readlines()[1:]]
        return f

    def parse_pokemon_data_file_line(line):
        temp_dict = {}
        temp_dict["LVL"] = int(line[1])
        temp_dict["XP"] = int(line[2])
        temp_dict["HP"] = int(line[3])
        temp_dict["ATK"] = int(line[4])
        temp_dict["DEF"] = int(line[5])
        temp_dict["SPATK"] = int(line[6])
        temp_dict["SPDEF"] = int(line[7])
        temp_dict["Move1"] = line[8]
        temp_dict["Move2"] = line[9]
        temp_dict["Move3"] = line[10]
        temp_dict["Move4"] = line[11]
        temp_dict["Move5"] = "Regular Attack"
        return temp_dict

    def load_base_pokemon_data(self):
        with open(os.path.join(os.getcwd(), "GameData", "PokemonBaseStats.txt")) as f:
            f = f.readlines()
        f = [line[:-1].split(",") for line in f][1:]
        base_dict = {}
        for line in f:
            if self.poke_id == line[0]:
                base_dict["Name"] = line[1]
                base_dict["HP"] = int(line[2])
                base_dict["ATK"] = int(line[3])
                base_dict["DEF"] = int(line[4])
                base_dict["SPATK"] = int(line[5])
                base_dict["SPDEF"] = int(line[6])
                base_dict["Type1"] = line[7]
                base_dict["Type2"] = line[8]
        return base_dict

    def pokemon_image_dict(self):
        def load(current_directory, img_id):
            direction_directory = os.path.join(current_directory, img_id)
            images = [file for file in os.listdir(direction_directory) if file != "Thumbs.db"]
            return [utils.scale(pygame.image.load(os.path.join(direction_directory, str(i) + ".png")), constants.POKE_SIZE) for i in
                    range(len(images))]

        full_dict = {}
        directory = os.path.join(os.getcwd(), "images", "Pokemon", self.poke_id)

        for image_type in [image_type for image_type in os.listdir(directory) if
                        image_type not in ["Thumbs.db", "Asleep"]]:  # ["Physical","Special","Motion","Hurt"]
            current_directory = os.path.join(directory, image_type)
            Dict = {direction.Direction.NORTH_WEST: load(current_directory, "1"),
                    direction.Direction.NORTH: load(current_directory, "2"),
                    direction.Direction.NORTH_EAST: [pygame.transform.flip(i, True, False) for i in load(current_directory, "1")],
                    direction.Direction.WEST: load(current_directory, "4"),
                    direction.Direction.EAST: [pygame.transform.flip(i, True, False) for i in load(current_directory, "4")],
                    direction.Direction.SOUTH_WEST: load(current_directory, "7"),
                    direction.Direction.SOUTH: load(current_directory, "8"),
                    direction.Direction.SOUTH_EAST: [pygame.transform.flip(i, True, False) for i in load(current_directory, "7")]
                    }
           
            full_dict[image_type] = Dict
        full_dict["Asleep"] = {}
        full_dict["Asleep"]["0"] = load(os.path.join(directory, "Asleep"), "0")
        return full_dict

    def spawn(self):
        possible_spawn = []
        for room in self.dungeon.dungeon_map.room_coords:
            for x, y in room:
                if (x, y) not in map(lambda s: s.grid_pos, all_sprites):
                    possible_spawn.append((x, y))
        self.grid_pos = random.choice(possible_spawn)
        self.blit_pos = (self.grid_pos[0] * constants.TILE_SIZE, self.grid_pos[1] * constants.TILE_SIZE)
        all_sprites.add(self)

    def move_on_grid(self, target):
        possible_directions = self.possible_directions()
        self.move_in_direction_of_minimal_distance(target, possible_directions)

        x = self.grid_pos[0] + self.direction.value[0]
        y = self.grid_pos[1] + self.direction.value[1]
        if self.direction in possible_directions:
            self.grid_pos = (x, y)

    def remove_corner_cutting_directions(self, possible_directions: list[direction.Direction]):
        x, y = self.grid_pos
        for d in direction.Direction.get_non_diagonal_directions():
            x_dir, y_dir = d.value

            if self.dungeon.dungeon_map.get_at(y + y_dir, x + x_dir) == tile.Tile.WALL:  # Prevents cutting corners when walls exist.
                if x_dir:
                    for k in range(len(possible_directions) - 1, -1, -1):
                        if x_dir == possible_directions[k].value[0]:
                            del possible_directions[k]
                elif y_dir:
                    for k in range(len(possible_directions) - 1, -1, -1):
                        if y_dir == possible_directions[k].value[1]:
                            del possible_directions[k]
        return possible_directions

    def remove_tile_directions(self, possible_directions: list[direction.Direction], tile: str) -> list[direction.Direction]:
        x, y = self.grid_pos
        possible_directions = [d for d in possible_directions if self.dungeon.dungeon_map.get_at(y + d.value[1], x + d.value[0]) != tile]
        return possible_directions

    def remove_occupied_directions(self, possible_directions: list[direction.Direction]):
        x, y = self.grid_pos
        possible_directions = [d for d in possible_directions if (x + d.value[0], y + d.value[1]) not in map(lambda s: s.grid_pos, all_sprites)]
        return possible_directions

    def possible_directions(self) -> list[direction.Direction]:  # lists the possible directions the pokemon may MOVE in.
        possible_directions = list(direction.Direction)
        if self.battle_info.type1 != "Ghost" and self.battle_info.type2 != "Ghost":
            possible_directions = self.remove_corner_cutting_directions(possible_directions)
            possible_directions = self.remove_tile_directions(possible_directions, tile.Tile.WALL)
        if self.battle_info.type1 != "Water" and self.battle_info.type2 != "Water":
            possible_directions = self.remove_tile_directions(possible_directions, tile.Tile.SECONDARY)
        possible_directions = self.remove_occupied_directions(possible_directions)
        return possible_directions  # Lists directions unoccupied and non-wall tiles(that aren't corner obstructed)

    def draw(self, x: int, y: int, display):
        a = self.blit_pos[0] + x
        b = self.blit_pos[1] + y
        scaled_shift = (constants.POKE_SIZE - constants.TILE_SIZE) // 2
        if self.poke_type in ["User", "Team"]:
            pygame.draw.ellipse(display, (255, 247, 0), (
                a + constants.TILE_SIZE * 4 / 24, b + constants.TILE_SIZE * 16 / 24, constants.TILE_SIZE * 16 / 24, constants.TILE_SIZE * 8 / 24))  # Yellow edge
            pygame.draw.ellipse(display, (222, 181, 0), (
                a + constants.TILE_SIZE * 5 / 24, b + constants.TILE_SIZE * 17 / 24, constants.TILE_SIZE * 14 / 24,
                constants.TILE_SIZE * 6 / 24))  # Lightbrown fade
            pygame.draw.ellipse(display, (165, 107, 0), (
                a + constants.TILE_SIZE * 6 / 24, b + constants.TILE_SIZE * 17 / 24, constants.TILE_SIZE * 12 / 24, constants.TILE_SIZE * 6 / 24))  # Brown ellipse
        else:
            pygame.draw.ellipse(display, constants.BLACK, (
                a + constants.TILE_SIZE * 4 / 24, b + constants.TILE_SIZE * 16 / 24, constants.TILE_SIZE * 16 / 24, constants.TILE_SIZE * 8 / 24))  # BlackShadow

        display.blit(self.current_image, (a - scaled_shift, b - scaled_shift))  # The pokemon image files are 200x200 px while tiles are 60x60. (200-60)/2 = 70 <- Centred when shifted by 70.

    ##############
    def vector_to_target(self, target):
        return (target.grid_pos[0] - self.grid_pos[0], target.grid_pos[1] - self.grid_pos[1])

    def distance_to_target(self, target):
        vector = self.vector_to_target(target)
        return (vector[0] * vector[0] + vector[1] * vector[1]) ** (0.5)

    def check_aggro(self, target):
        distance = self.distance_to_target(target)
        vector = self.vector_to_target(target)
        for room in self.dungeon.dungeon_map.room_coords:
            if self.grid_pos in room and target.grid_pos in room:  # Pokemon aggro onto the user if in the same room
                same_room = True
                break
            else:
                same_room = False

        if distance <= constants.AGGRO_RANGE or same_room:  # Pokemon also aggro if withing a certain range AGGRORANGE
            return distance, vector, True
        else:
            return None, None, False

    def move_in_direction_of_minimal_distance(self, target, possible_directions: list[direction.Direction]):
        if not target:
            return
        elif target.grid_pos == (self.grid_pos[0] + self.direction.value[0], self.grid_pos[1] + self.direction.value[1]):
            return  # Already facing target, no need to change direction
        distance, vector, aggro = self.check_aggro(target)
        if aggro:
            if distance < 2:
                for dir in direction.Direction:
                    if dir.value == vector:
                        self.direction = dir
                        return
            self.direction = sorted(possible_directions, key=(lambda d: (self.grid_pos[0] - target.grid_pos[0] + d.value[0])**2 + (self.grid_pos[1] - target.grid_pos[1] + d.value[1])**2))[0]
        else:  # Face a random, but valid direction if not aggro
            ## TO DO: error when len(possible_directions) == 0
            self.direction = random.choice(possible_directions)

    ################
    # ANIMATIONS
    def motion_animation(self, motion_time_left, time_for_one_tile):
        if self.blit_pos != (self.grid_pos[0] * constants.TILE_SIZE, self.grid_pos[1] * constants.TILE_SIZE):
            images = self.image_dict["Motion"][self.direction]
            step_size = 1 / len(images)
            for i in range(len(images)):
                if step_size * i <= motion_time_left / time_for_one_tile < step_size * (i + 1):
                    self.current_image = self.image_dict["Motion"][self.direction][(i + 2) % len(images)]

            x = (self.grid_pos[0] - (self.direction.value[0] * motion_time_left / time_for_one_tile)) * constants.TILE_SIZE
            y = (self.grid_pos[1] - (self.direction.value[1] * motion_time_left / time_for_one_tile)) * constants.TILE_SIZE
            self.blit_pos = (x, y)
            if self.blit_pos == (self.grid_pos[0] * constants.TILE_SIZE, self.grid_pos[1] * constants.TILE_SIZE):
                self.current_image = self.image_dict["Motion"][self.direction][0]

    def do_animation(self, effect, attack_time_left, time_for_one_tile, display):
        if effect == "Damage":
            self.hurt_animation(attack_time_left, time_for_one_tile)
        elif effect in ["ATK+", "ATK-", "DEF+", "DEF-", "SPATK+", "SPATK-", "SPDEF+", "SPDEF-"]:
            self.stat_animation(effect, attack_time_left, time_for_one_tile, display)
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
            x = (self.grid_pos[0] + (self.direction.value[0]) * 2 * (
                    0.25 - (0.5 - (attack_time_left / time_for_one_tile)) ** 2)) * constants.TILE_SIZE
            y = (self.grid_pos[1] + (self.direction.value[1]) * 2 * (
                    0.25 - (0.5 - (attack_time_left / time_for_one_tile)) ** 2)) * constants.TILE_SIZE
            self.blit_pos = (x, y)

    def stat_animation(self, effect, attack_time_left, time_for_one_tile, display):
        stat = effect[:-1]
        action = effect[-1]
        images = LoadImages.stats_animation_dict[stat][action]
        step_size = 1 / len(images)
        for sprite in all_sprites:
            if sprite.poke_type == "User":
                x = self.blit_pos[0] + constants.DISPLAY_WIDTH / 2 - sprite.blit_pos[0]
                y = self.blit_pos[1] + constants.DISPLAY_HEIGHT / 2 - sprite.blit_pos[1]
                break
        for i in range(len(images)):
            if step_size * i <= attack_time_left / time_for_one_tile < step_size * (i + 1):
                display.blit(images[i], (x, y))
                break

    ################
    def miss(self, move_accuracy, evasion):
        i = random.randint(0, 99)
        raw_accuracy = self.battle_info.status["ACC"] / 100 * move_accuracy
        if round(raw_accuracy - evasion) > i:
            return False
        else:
            return True

    def activate(self, move_index):
        if move_index == None:
            return []
        move_used = self.battle_info.move_set[move_index]
        steps = []
        if move_used.pp != 0:
            move_used.pp -= 1

            msg = self.battle_info.name + " used " + move_used.name
            textbox.text_box.append(text.Text(msg))

            for i in range(len(move_used.effects)):
                Dict = {}
                effect = move_used.effects[i]
                move_range = move_used.ranges[i]
                target_type = move_used.target_type[i]
                targets = self.find_possible_targets(target_type)
                targets = self.filter_out_of_range_targets(targets, move_range, move_used.cuts_corners)
                if targets:
                    Dict["Targets"] = targets
                    Dict["Effect"] = effect
                    steps.append(Dict)
                    self.activate_effect(move_used, i, targets)
                else:
                    if i == 0:
                        msg = "The move failed."
                        textbox.text_box.append(text.Text(msg))
                    break
        else:
            msg = "You have ran out of PP for this move."
            textbox.text_box.append(text.Text(msg))

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
                textbox.text_box.append(text.Text(msg))
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
                    textbox.text_box.append(text.Text(msg))

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

    def filter_out_of_range_targets(self, targets, move_range, cuts_corners):
        if move_range == "0":
            return [self]

        possible_directions = list(direction.Direction)
        if not cuts_corners:
            possible_directions = self.remove_corner_cutting_directions(possible_directions)

        if move_range == "1" or move_range == "2" or move_range == "10":  # Front
            possible_directions = self.remove_tile_directions(possible_directions, tile.Tile.WALL)
            if self.direction in possible_directions:
                for n in range(1, int(move_range) + 1):
                    for target in targets:
                        x = self.grid_pos[0] + n * self.direction.value[0]
                        y = self.grid_pos[1] + n * self.direction.value[1]
                        if self.dungeon.dungeon_map.get_at(y, x) == tile.Tile.WALL:
                            return []
                        if target.grid_pos == (x, y):
                            return [target]

        if move_range == "S" or move_range == "R":  # Surrounding
            new_targets = []
            for target in targets:
                for dir in possible_directions:
                    x = self.grid_pos[0] + dir.value[0]
                    y = self.grid_pos[1] + dir.value[1]
                    if target.grid_pos == (x, y):
                        new_targets.append(target)
            if move_range == "S":
                return new_targets
            else:  # Range == "R"
                x, y = self.grid_pos

                if self.dungeon.dungeon_map.get_at(y, x) == tile.Tile.GROUND:
                    for room in self.dungeon.dungeon_map.room_coords:
                        if (x, y) in room:
                            possible_directions = room
                            break
                    for target in targets:
                        if target.grid_pos in possible_directions:
                            new_targets.append(target)
                new_targets = utils.remove_duplicates(new_targets)
                return new_targets
        return []
