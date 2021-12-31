import constants
import direction
import damage_chart
import LoadImages
import move
import os
import pokemon_battle_info
import pygame.draw
import pygame.image
import pygame.sprite
import pygame.transform
import random
import pokemonsprite
import tile
import text
import textbox
import utils
import xml.etree.ElementTree as ET

class Pokemon:  # poke_type {User, Teammate, Enemy, Other..}
    REGENRATION_RATE = 2

    def __init__(self, poke_id: str, poke_type: str, dungeon):
        self.poke_id = poke_id
        self.poke_type = poke_type
        self.dungeon = dungeon
        self.image_dict = pokemonsprite.PokemonSprite(self.poke_id).image_dict
        self.load_pokemon_object()
        self.direction = direction.Direction.SOUTH
        self.has_turn = True
        self.current_image = self.image_dict["Walk"][self.direction][0]

    def load_pokemon_object(self):
        if self.poke_type in ("User", "Team"):
            specific_pokemon_data = self.load_user_specific_pokemon_data()
        elif self.poke_type == "Enemy":
            for foe in self.dungeon.foes:
                if foe.poke_id == self.poke_id:
                    specific_pokemon_data = foe

        generic_data = GenericPokemon(self.poke_id)

        xp = specific_pokemon_data.xp
        level = xp  # TO DO: Calculation based on xp and generic_data.root
        hp = generic_data.hp + specific_pokemon_data.hp
        ATK = generic_data.attack + specific_pokemon_data.attack
        DEF = generic_data.defense + specific_pokemon_data.defense
        SPATK = generic_data.sp_attack + specific_pokemon_data.sp_attack
        SPDEF = generic_data.sp_defense + specific_pokemon_data.sp_defense
        move_set = specific_pokemon_data.moveset
        base = {
            "HP": hp,
            "ATK": ATK,
            "DEF": DEF,
            "SPATK": SPATK,
            "SPDEF": SPDEF,
            "ACC": 100,
            "EVA": 0,
            "Regen": True
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
        }

        self.battle_info = pokemon_battle_info.PokemonBattleInfo(
            self.poke_id,
            name=generic_data.name,
            level=level,
            xp=xp,
            type1=generic_data.primary_type,
            type2=generic_data.secondary_type,
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
        specific_data = SpecificPokemon(line[0])
        specific_data.xp = int(line[2])
        specific_data.hp = int(line[3])
        specific_data.attack = int(line[4])
        specific_data.defense = int(line[5])
        specific_data.sp_attack = int(line[6])
        specific_data.sp_defense = int(line[7])
        specific_data.moveset.append(move.Move(line[8]))
        specific_data.moveset.append(move.Move(line[9]))
        specific_data.moveset.append(move.Move(line[10]))
        specific_data.moveset.append(move.Move(line[11]))
        specific_data.moveset.append(move.Move("Regular Attack"))
        return specific_data

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
        possible_directions = [d for d in possible_directions if (x + d.value[0], y + d.value[1]) not in map(lambda s: s.grid_pos, self.dungeon.all_sprites)]
        return possible_directions

    def possible_directions(self) -> list[direction.Direction]:  # lists the possible directions the pokemon may MOVE in.
        possible_directions = list(direction.Direction)
        if self.battle_info.type1 != damage_chart.Type.GHOST and self.battle_info.type2 != damage_chart.Type.GHOST:
            possible_directions = self.remove_corner_cutting_directions(possible_directions)
            possible_directions = self.remove_tile_directions(possible_directions, tile.Tile.WALL)
        if self.battle_info.type1 != damage_chart.Type.WATER and self.battle_info.type2 != damage_chart.Type.WATER:
            possible_directions = self.remove_tile_directions(possible_directions, tile.Tile.SECONDARY)
        possible_directions = self.remove_occupied_directions(possible_directions)
        return possible_directions  # Lists directions unoccupied and non-wall tiles(that aren't corner obstructed)

    def draw(self, x: int, y: int, display):
        a = self.blit_pos[0] + x
        b = self.blit_pos[1] + y
        shift_x = (self.current_image.get_width() - constants.TILE_SIZE) // 2
        shift_y = (self.current_image.get_height() - constants.TILE_SIZE) // 2
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

        display.blit(self.current_image, (a - shift_x, b - shift_y))

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
            images = self.image_dict["Walk"][self.direction]
            step_size = 1 / len(images)
            for i in range(len(images)):
                if step_size * i <= motion_time_left / time_for_one_tile < step_size * (i + 1):
                    self.current_image = self.image_dict["Walk"][self.direction][(i + 2) % len(images)]

            x = (self.grid_pos[0] - (self.direction.value[0] * motion_time_left / time_for_one_tile)) * constants.TILE_SIZE
            y = (self.grid_pos[1] - (self.direction.value[1] * motion_time_left / time_for_one_tile)) * constants.TILE_SIZE
            self.blit_pos = (x, y)
            if self.blit_pos == (self.grid_pos[0] * constants.TILE_SIZE, self.grid_pos[1] * constants.TILE_SIZE):
                self.current_image = self.image_dict["Walk"][self.direction][0]

    def do_animation(self, effect, attack_time_left, time_for_one_tile, display):
        if effect == "Damage":
            self.hurt_animation(attack_time_left, time_for_one_tile)
        elif effect in ["ATK+", "ATK-", "DEF+", "DEF-", "SPATK+", "SPATK-", "SPDEF+", "SPDEF-"]:
            self.stat_animation(effect, attack_time_left, time_for_one_tile, display)

    def hurt_animation(self, attack_time_left, time_for_one_tile):
        if self.battle_info.status["HP"] == 0:
            upper_bound = 1.5
        else:
            upper_bound = 0.85
        if 0.15 < attack_time_left / time_for_one_tile <= upper_bound:
            self.current_image = self.image_dict["Hurt"][self.direction][0]
        else:
            self.current_image = self.image_dict["Walk"][self.direction][0]

    def attack_animation(self, attack_index, attack_time_left, time_for_one_tile):
        category = self.battle_info.move_set[attack_index].category
        if category == "Physical":
            image_type = "Attack"
        if category == "Special":
            image_type = "Attack"
        elif category == "Status":
            category = "Special"
            image_type = "Charge"
        else:
            image_type = "Idle"

        images = self.image_dict[image_type][self.direction]
        step_size = 1 / len(images)
        for i in range(len(images)):
            if step_size * i <= attack_time_left / time_for_one_tile < step_size * (i + 1):
                self.current_image = self.image_dict[image_type][self.direction][i]

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
        for sprite in self.dungeon.all_sprites:
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
        return round(raw_accuracy - evasion) <= i

    def activate(self, move_index):
        if move_index == None:
            return []
        move_used = self.battle_info.move_set[move_index]
        steps = []
        if move_used.pp != 0:
            move_used.pp -= 1

            msg = self.battle_info.name + " used " + move_used.name
            textbox.message_log.append(text.Text(msg))

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
                        textbox.message_log.append(text.Text(msg))
                    break
        else:
            msg = "You have ran out of PP for this move."
            textbox.message_log.append(text.Text(msg))

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
                textbox.message_log.append(text.Text(msg))
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

    def find_possible_targets(self, target_type):
        allies = [sprite for sprite in self.dungeon.all_sprites if sprite.poke_type in ("User", "Team")]
        enemies = [sprite for sprite in self.dungeon.all_sprites if sprite.poke_type == "Enemy"]
        if self.poke_type == "Enemy":
            allies, enemies = enemies, allies

        if target_type == "Self":
            return [self]
        elif target_type == "All":
            return [sprite for sprite in self.dungeon.all_sprites]
        elif target_type == "Allies":
            return allies
        elif target_type == "Enemies":
            return enemies
        elif target_type == "Non-Self":
            return [sprite for sprite in self.dungeon.all_sprites if sprite != self]

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

class GenericPokemon:
    def __init__(self, poke_id):
        self.poke_id = poke_id
        self.parse_file()

    def parse_file(self):
        file = os.path.join(os.getcwd(), "GameData", "pokemon", self.poke_id + ".xml")
        tree = ET.parse(file)
        self.root = tree.getroot()
        self.name = self.root.find("Strings").find("English").find("Name").text
        base_stats = self.root.find("GenderedEntity").find("BaseStats")
        self.hp = int(base_stats.find("HP").text)
        self.attack = int(base_stats.find("Attack").text)
        self.defense = int(base_stats.find("Defense").text)
        self.sp_attack = int(base_stats.find("SpAttack").text)
        self.sp_defense = int(base_stats.find("SpDefense").text)
        self.primary_type = damage_chart.Type(int(self.root.find("GenderedEntity").find("PrimaryType").text))
        self.secondary_type = damage_chart.Type(int(self.root.find("GenderedEntity").find("SecondaryType").text))

class SpecificPokemon:
    def __init__(self, poke_id):
        self.poke_id = poke_id
        self.xp = 0
        self.hp = 0
        self.attack = 0
        self.defense = 0
        self.sp_attack = 0
        self.sp_defense = 0
        self.moveset = []