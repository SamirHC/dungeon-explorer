from LoadImages import *
from textbox import *
from utils import *
from dungeon_map import DungeonMap
import random
from tile import Tile
from text import Text
from pokemon_battle_info import PokemonBattleInfo
from move import Move

all_sprites = p.sprite.Group()

def load_base_pokemon_data():
    pokemon_base_stats_dict = {}
    with open(os.path.join(os.getcwd(), "GameData", "PokemonBaseStats.txt")) as f:
        f = f.readlines()
    f = [line[:-1].split(",") for line in f][1:]
    for poke in f:
        try:
            temp_dict = {}
            poke_id = poke[0]
            temp_dict["Name"] = poke[1]
            temp_dict["HP"] = int(poke[2])
            temp_dict["ATK"] = int(poke[3])
            temp_dict["DEF"] = int(poke[4])
            temp_dict["SPATK"] = int(poke[5])
            temp_dict["SPDEF"] = int(poke[6])
            temp_dict["Type1"] = poke[7]
            temp_dict["Type2"] = poke[8]
            pokemon_base_stats_dict[poke_id] = temp_dict
        except:
            pass
    return pokemon_base_stats_dict


pokemon_base_stats_dict = load_base_pokemon_data()


def load_user_specific_pokemon_data():
    pokemon_specific_dict = {}
    d = os.path.join(os.getcwd(), "UserData", "UserTeamData.txt")
    with open(d) as f:
        f = f.readlines()
    f = [line[:-1].split(",") for line in f][1:]
    for poke in f:
        temp_dict = {}
        poke_id = poke[0]
        temp_dict["LVL"] = int(poke[1])
        temp_dict["XP"] = int(poke[2])
        temp_dict["HP"] = int(poke[3])
        temp_dict["ATK"] = int(poke[4])
        temp_dict["DEF"] = int(poke[5])
        temp_dict["SPATK"] = int(poke[6])
        temp_dict["SPDEF"] = int(poke[7])
        temp_dict["Move1"] = poke[8]
        temp_dict["Move2"] = poke[9]
        temp_dict["Move3"] = poke[10]
        temp_dict["Move4"] = poke[11]
        temp_dict["Move5"] = "Regular Attack"
        pokemon_specific_dict[poke_id] = temp_dict
    return pokemon_specific_dict


user_specific_pokemon_dict = load_user_specific_pokemon_data()


def load_dungeon_specific_pokemon_data():
    Dict = {}
    d = [dungeon for dungeon in os.listdir(os.path.join(os.getcwd(), "GameData", "Dungeons")) if dungeon != "Thumbs.db"]
    for dungeon in d:
        dungeon_dict = {}
        file = os.path.join(os.getcwd(), "GameData", "Dungeons", dungeon, "PokemonData.txt")
        with open(file) as f:
            f = f.readlines()
        f = [line[:-1].split(",") for line in f][1:]
        for poke in f:
            temp_dict = {}
            poke_id = poke[0]
            temp_dict["LVL"] = int(poke[1])
            temp_dict["XP"] = int(poke[2])
            temp_dict["HP"] = int(poke[3])
            temp_dict["ATK"] = int(poke[4])
            temp_dict["DEF"] = int(poke[5])
            temp_dict["SPATK"] = int(poke[6])
            temp_dict["SPDEF"] = int(poke[7])
            temp_dict["Move1"] = poke[8]
            temp_dict["Move2"] = poke[9]
            temp_dict["Move3"] = poke[10]
            temp_dict["Move4"] = poke[11]
            temp_dict["Move5"] = "Regular Attack"
            dungeon_dict[poke_id] = temp_dict
        Dict[dungeon] = dungeon_dict
    return Dict


dungeon_specific_pokemon_dict = load_dungeon_specific_pokemon_data()

def load_pokemon_object(poke_id, poke_type, dungeon=None):
    if poke_type == "User" or poke_type == "Team":
        specific_pokemon_data = user_specific_pokemon_dict[poke_id]
    elif poke_type == "Enemy" and dungeon:
        specific_pokemon_data = dungeon_specific_pokemon_dict[dungeon][poke_id]

    level = specific_pokemon_data["LVL"]
    xp = specific_pokemon_data["XP"]
    hp = pokemon_base_stats_dict[poke_id]["HP"] + specific_pokemon_data["HP"]
    ATK = pokemon_base_stats_dict[poke_id]["ATK"] + specific_pokemon_data["ATK"]
    DEF = pokemon_base_stats_dict[poke_id]["DEF"] + specific_pokemon_data["DEF"]
    SPATK = pokemon_base_stats_dict[poke_id]["SPATK"] + specific_pokemon_data["SPATK"]
    SPDEF = pokemon_base_stats_dict[poke_id]["SPDEF"] + specific_pokemon_data["SPDEF"]
    move_set = []
    for i in range(1, 6):
        current_move = specific_pokemon_data["Move" + str(i)]
        move_set.append(Move(current_move))

    image_dict = pokemon_image_dict(poke_id)
    base_dict = {"HP": hp,
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
    status_dict = {"HP": hp,
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
    return Pokemon(image_dict=image_dict,
                   poke_type=poke_type,
                   battle_info=PokemonBattleInfo(poke_id,
                                                name=pokemon_base_stats_dict[poke_id]["Name"],
                                                level=level,
                                                xp=xp,
                                                type1=pokemon_base_stats_dict[poke_id]["Type1"],
                                                type2=pokemon_base_stats_dict[poke_id]["Type2"],
                                                base=base_dict,
                                                status=status_dict,
                                                move_set=move_set
                                                )
                   )

class Pokemon(p.sprite.Sprite):  # poke_type {User, Teammate, Enemy, Other..}
    def __init__(self, image_dict, poke_type, battle_info=None):
        super().__init__()
        self.image_dict = image_dict
        self.direction = (0, 1)
        self.turn = True
        self.poke_type = poke_type
        self.battle_info = battle_info
        for image_type in self.image_dict:
            for direction in self.image_dict[image_type]:
                for image in self.image_dict[image_type][direction]:
                    image.set_colorkey(TRANS)
        self.current_image = image_dict["Motion"][self.direction][0]


    def spawn(self, floor: DungeonMap):
        possible_spawn = []
        for room in floor.room_coords:
            for x, y in room:
                if (x, y) not in map(lambda s: s.grid_pos, all_sprites):
                    possible_spawn.append((x, y))
        self.grid_pos = random.choice(possible_spawn)
        self.blit_pos = (self.grid_pos[0] * TILE_SIZE, self.grid_pos[1] * TILE_SIZE)
        all_sprites.add(self)

    def move_on_grid(self, map, target):
        possible_directions = self.possible_directions(map)
        self.move_in_direction_of_minimal_distance(target, map, possible_directions)

        x = self.grid_pos[0] + self.direction[0]
        y = self.grid_pos[1] + self.direction[1]
        if self.direction in possible_directions:
            self.grid_pos = (x, y)

    def remove_corner_cutting_directions(self, possible_directions, map):
        x, y = self.grid_pos
        for i in [(-1, 0), (0, -1), (1, 0), (0, 1)]:
            x_dir, y_dir = i[0], i[1]

            if map.floor[y + y_dir][x + x_dir] == Tile.WALL:  # Prevents cutting corners when walls exist.
                if x_dir:
                    for k in range(len(possible_directions) - 1, -1, -1):
                        if x_dir == possible_directions[k][0]:
                            del possible_directions[k]
                elif y_dir:
                    for k in range(len(possible_directions) - 1, -1, -1):
                        if y_dir == possible_directions[k][1]:
                            del possible_directions[k]
        return possible_directions

    def remove_tile_directions(self, possible_directions: list[tuple[int, int]], map: DungeonMap, tile: str) -> list[tuple[int, int]]:
        x, y = self.grid_pos
        for i in range(len(possible_directions) - 1, -1, -1):  # Prevents walking through non-ground tiles and through other pokemon.
            xdir, ydir = possible_directions[i][0], possible_directions[i][1]
            if map.floor[y + ydir][x + xdir] == tile:
                del possible_directions[i]
        return possible_directions

    def possible_directions(self, map: DungeonMap) -> list[tuple[int, int]]:  # lists the possible directions the pokemon may MOVE in.
        possible_directions = [(i, j) for i in range(-1, 2) for j in range(-1, 2)]
        if self.battle_info.type1 != "Ghost" and self.battle_info.type2 != "Ghost":
            possible_directions = self.remove_corner_cutting_directions(possible_directions, map)
            possible_directions = self.remove_tile_directions(possible_directions, map, Tile.WALL)
        if self.battle_info.type1 != "Water" and self.battle_info.type2 != "Water":
            possible_directions = self.remove_tile_directions(possible_directions, map, Tile.SECONDARY)

        for sprite in all_sprites:
            if 1 <= self.distance_to_target(sprite, self.grid_pos) < 2:
                if self.vector_to_target(sprite, self.grid_pos) in possible_directions:
                    possible_directions.remove(self.vector_to_target(sprite, self.grid_pos))

        return possible_directions  # Lists directions unoccupied and non-wall tiles(that aren't corner obstructed)

    def draw(self, x: int, y: int):
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
    def vector_to_target(self, target, position: tuple[int, int]):
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

            new_direction = self.direction

            for direction in possible_directions:
                surrounding_pos = (self.grid_pos[0] + direction[0], self.grid_pos[1] + direction[1])
                new_distance = self.distance_to_target(target, surrounding_pos)

                if new_distance < distance:
                    distance = new_distance
                    new_direction = direction

            self.direction = new_direction

        else:  # Face a random, but valid direction if not aggro
            self.direction = random.choice(possible_directions)

    ################
    # ANIMATIONS
    def motion_animation(self, motion_time_left, time_for_one_tile):
        if self.blit_pos != (self.grid_pos[0] * TILE_SIZE, self.grid_pos[1] * TILE_SIZE):
            images = self.image_dict["Motion"][self.direction]
            step_size = 1 / len(images)
            for i in range(len(images)):
                if step_size * i <= motion_time_left / time_for_one_tile < step_size * (i + 1):
                    self.current_image = self.image_dict["Motion"][self.direction][(i + 2) % len(images)]

            x = (self.grid_pos[0] - (self.direction[0] * motion_time_left / time_for_one_tile)) * TILE_SIZE
            y = (self.grid_pos[1] - (self.direction[1] * motion_time_left / time_for_one_tile)) * TILE_SIZE
            self.blit_pos = (x, y)
            if self.blit_pos == (self.grid_pos[0] * TILE_SIZE, self.grid_pos[1] * TILE_SIZE):
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
            x = (self.grid_pos[0] + (self.direction[0]) * 2 * (
                    0.25 - (0.5 - (attack_time_left / time_for_one_tile)) ** 2)) * TILE_SIZE
            y = (self.grid_pos[1] + (self.direction[1]) * 2 * (
                    0.25 - (0.5 - (attack_time_left / time_for_one_tile)) ** 2)) * TILE_SIZE
            self.blit_pos = (x, y)

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
        i = random.randint(0, 99)
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
            text_box.append(Text(msg))

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
                        text_box.append(Text(msg))
                    break
        else:
            msg = "You have ran out of PP for this move."
            text_box.append(Text(msg))

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
                text_box.append(Text(msg))
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
                    text_box.append(Text(msg))

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
            possible_directions = self.remove_tile_directions(possible_directions, map, Tile.WALL)
            if self.direction in possible_directions:
                for n in range(1, int(move_range) + 1):
                    for target in targets:
                        x = self.grid_pos[0] + n * self.direction[0]
                        y = self.grid_pos[1] + n * self.direction[1]
                        if map.floor[y][x] == Tile.WALL:
                            return []
                        if target.grid_pos == (x, y):
                            return [target]

        if move_range == "S" or move_range == "R":  # Surrounding
            new_targets = []
            for target in targets:
                for direction in possible_directions:
                    x = self.grid_pos[0] + direction[0]
                    y = self.grid_pos[1] + direction[1]
                    if target.grid_pos == (x, y):
                        new_targets.append(target)
            if move_range == "S":
                return new_targets
            else:  # Range == "R"
                x, y = self.grid_pos

                if map.floor[y][x] == Tile.GROUND:
                    for room in map.room_coords:
                        if (x, y) in room:
                            possible_directions = room
                            break
                    for target in targets:
                        if target.grid_pos in possible_directions:
                            new_targets.append(target)
                new_targets = remove_duplicates(new_targets)
                return new_targets
        return []
