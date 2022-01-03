import animation
import constants
import direction
import damage_chart
import LoadImages
import move
import os
import pygame
import pygame.draw
import pygame.image
import pygame.sprite
import pygame.transform
import random
import pokemonsprite
import tile
import utils
import xml.etree.ElementTree as ET

class BattleStats:
    def __init__(self):
        self.xp = 0
        self.level = 0
        self.hp = 0
        self.attack = 0
        self.defense = 0
        self.sp_attack = 0
        self.sp_defense = 0
        self.accuracy = 100
        self.evasion = 0

class PokemonType:
    def __init__(self, primary_type: damage_chart.Type, secondary_type: damage_chart.Type):
        self.primary_type = primary_type
        self.secondary_type = secondary_type

    @property
    def types(self) -> tuple(damage_chart.Type):
        return (self.primary_type, self.secondary_type)

    def is_type(self, type: damage_chart.Type) -> bool:
        return type in self.types

    def get_damage_multiplier(self, move_type: damage_chart.Type) -> float:
        primary_multiplier = damage_chart.TypeChart.get_multiplier(move_type, self.primary_type)
        secondary_multiplier = damage_chart.TypeChart.get_multiplier(move_type, self.secondary_type)
        return primary_multiplier * secondary_multiplier

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
        self.base_stats = BattleStats()
        self.base_stats.hp = int(base_stats.find("HP").text)
        self.base_stats.attack = int(base_stats.find("Attack").text)
        self.base_stats.defense = int(base_stats.find("Defense").text)
        self.base_stats.sp_attack = int(base_stats.find("SpAttack").text)
        self.base_stats.sp_defense = int(base_stats.find("SpDefense").text)
        primary_type = damage_chart.Type(int(self.root.find("GenderedEntity").find("PrimaryType").text))
        secondary_type = damage_chart.Type(int(self.root.find("GenderedEntity").find("SecondaryType").text))
        self.type = PokemonType(primary_type, secondary_type)

    def get_stats_growth(self, xp: int) -> BattleStats:
        stats_growth_node = self.root.find("StatsGrowth")
        stats_growth = BattleStats()
        for level in stats_growth_node.findall("Level"):
            if int(level.find("RequiredExp").text) <= xp:
                stats_growth.level += 1
                stats_growth.hp += int(level.find("HP").text)
                stats_growth.attack += int(level.find("Attack").text)
                stats_growth.sp_attack += int(level.find("SpAttack").text)
                stats_growth.defense += int(level.find("Defense").text)
                stats_growth.sp_defense += int(level.find("SpDefense").text)
        return stats_growth

class SpecificPokemon:
    def __init__(self, poke_id):
        self.poke_id = poke_id
        self.stat_boosts = BattleStats()
        self.moveset = Moveset()

class Moveset:
    MAX_MOVES = 4
    REGULAR_ATTACK = move.Move("0000")

    def __init__(self, moveset=[]):
        self.moveset = moveset

    def knows_move(self, m: move.Move) -> bool:
        return m in self.moveset

class Pokemon:
    REGENRATION_RATE = 2
    AGGRO_RANGE = 5

    def __init__(self, poke_id: str, poke_type: str, dungeon):
        self.poke_id = poke_id
        self.poke_type = poke_type
        self.dungeon = dungeon
        self.animations = pokemonsprite.PokemonSprite(self.poke_id).animations
        self.load_pokemon_object()
        self.direction = direction.Direction.SOUTH
        self.has_turn = True
        self.animation_name = "Walk"

    @property
    def current_image(self) -> pygame.Surface:
        return self.animation.get_current_frame()

    @property
    def animation(self) -> animation.Animation:
        return self.animations[self.animation_name][self.direction]

    def load_pokemon_object(self):
        if self.poke_type in ("User", "Team"):
            specific_pokemon_data = self.load_user_specific_pokemon_data()
        elif self.poke_type == "Enemy":
            for foe in self.dungeon.possible_enemies:
                if foe.poke_id == self.poke_id:
                    specific_pokemon_data = foe

        generic_data = GenericPokemon(self.poke_id)
        self._name = generic_data.name
        self._type = generic_data.type

        actual_stats = generic_data.get_stats_growth(specific_pokemon_data.stat_boosts.xp)
        actual_stats.hp += generic_data.base_stats.hp + specific_pokemon_data.stat_boosts.hp
        actual_stats.attack += generic_data.base_stats.attack + specific_pokemon_data.stat_boosts.attack
        actual_stats.defense += generic_data.base_stats.defense + specific_pokemon_data.stat_boosts.defense
        actual_stats.sp_attack += generic_data.base_stats.sp_attack + specific_pokemon_data.stat_boosts.sp_attack
        actual_stats.sp_defense += generic_data.base_stats.sp_defense + specific_pokemon_data.stat_boosts.sp_defense
        self.actual_stats = actual_stats

        self.move_set = specific_pokemon_data.moveset

        self.status_dict = {
            "HP": actual_stats.hp,
            "ATK": 10,
            "DEF": 10,
            "SPATK": 10,
            "SPDEF": 10,
            "ACC": 100,
            "EVA": 0,
            "Regen": 1,
        }

    @property
    def name(self) -> str:
        return self._name

    @property
    def type(self) -> PokemonType:
        return self._type
    
    @property
    def max_hp(self) -> int:
        return self.actual_stats.hp
    
    @property
    def attack(self) -> int:
        return self.actual_stats.attack

    @property
    def sp_attack(self) -> int:
        return self.actual_stats.sp_attack

    @property
    def defense(self) -> int:
        return self.actual_stats.defense

    @property
    def sp_defense(self) -> int:
        return self.actual_stats.sp_defense

    @property
    def level(self) -> int:
        return self.actual_stats.level

    @property
    def xp(self) -> int:
        return self.actual_stats.xp

    @property
    def hp(self) -> int:
        return self.status_dict["HP"]
    @hp.setter
    def hp(self, hp: int):
        if hp < 0:
            self.status_dict["HP"] = 0
        elif hp > self.max_hp:
            self.status_dict["HP"] = self.max_hp
        else:
            self.status_dict["HP"] = hp

    @property
    def attack_status(self) -> int:
        return self.status_dict["ATK"]
    @attack_status.setter
    def attack_status(self, attack_status):
        if attack_status < 0:
            self.status_dict["ATK"] = 0
        elif attack_status > 20:
            self.status_dict["ATK"] = 20
        else:
            self.status_dict["ATK"] = attack_status

    @property
    def defense_status(self) -> int:
        return self.status_dict["DEF"]
    @defense_status.setter
    def defense_status(self, defense_status):
        if defense_status < 0:
            self.status_dict["DEF"] = 0
        elif defense_status > 20:
            self.status_dict["DEF"] = 20
        else:
            self.status_dict["DEF"] = defense_status

    @property
    def sp_attack_status(self) -> int:
        return self.status_dict["SPATK"]
    @sp_attack_status.setter
    def sp_attack_status(self, sp_attack_status):
        if sp_attack_status < 0:
            self.status_dict["SPATK"] = 0
        elif sp_attack_status > 20:
            self.status_dict["SPATK"] = 20
        else:
            self.status_dict["SPATK"] = sp_attack_status
    
    @property
    def sp_defense_status(self) -> int:
        return self.status_dict["SPDEF"]
    @sp_defense_status.setter
    def sp_defense_status(self, sp_defense_status):
        if sp_defense_status < 0:
            self.status_dict["SPDEF"] = 0
        elif sp_defense_status > 20:
            self.status_dict["SPDEF"] = 20
        else:
            self.status_dict["SPDEF"] = sp_defense_status

    @property
    def accuracy_status(self) -> int:
        return self.status_dict["ACC"]
    @accuracy_status.setter
    def accuracy_status(self, accuracy_status):
        if accuracy_status < 0:
            self.status_dict["ACC"] = 0
        elif accuracy_status > 20:
            self.status_dict["ACC"] = 20
        else:
            self.status_dict["ACC"] = accuracy_status

    @property
    def evasion_status(self) -> int:
        return self.status_dict["EVA"]
    @evasion_status.setter
    def evasion_status(self, evasion_status):
        if evasion_status < 0:
            self.status_dict["EVA"] = 0
        elif evasion_status > 20:
            self.status_dict["EVA"] = 20
        else:
            self.status_dict["EVA"] = evasion_status

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
        specific_data.stat_boosts.xp = int(line[1])
        specific_data.stat_boosts.hp = int(line[2])
        specific_data.stat_boosts.attack = int(line[3])
        specific_data.stat_boosts.defense = int(line[4])
        specific_data.stat_boosts.sp_attack = int(line[5])
        specific_data.stat_boosts.sp_defense = int(line[6])
        specific_data.moveset = Moveset([move.Move(m) for m in line[7:]])
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
        if not self.type.is_type(damage_chart.Type.GHOST):
            possible_directions = self.remove_corner_cutting_directions(possible_directions)
            possible_directions = self.remove_tile_directions(possible_directions, tile.Tile.WALL)
        if not self.type.is_type(damage_chart.Type.WATER):
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

        if distance <= Pokemon.AGGRO_RANGE or same_room:  # Pokemon also aggro if withing a certain range AGGRORANGE
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
            if len(possible_directions):
                self.direction = random.choice(possible_directions)

    ################
    # ANIMATIONS
    def motion_animation(self, motion_time_left, time_for_one_tile):
        if self.blit_pos != (self.grid_pos[0] * constants.TILE_SIZE, self.grid_pos[1] * constants.TILE_SIZE):
            self.animation_name = "Walk"
            step_size = 1 / len(self.animation.frames)
            for i in range(len(self.animation.frames)):
                if step_size * i <= motion_time_left / time_for_one_tile < step_size * (i + 1):
                    self.animation.index = i

            x = (self.grid_pos[0] - (self.direction.value[0] * motion_time_left / time_for_one_tile)) * constants.TILE_SIZE
            y = (self.grid_pos[1] - (self.direction.value[1] * motion_time_left / time_for_one_tile)) * constants.TILE_SIZE
            self.blit_pos = (x, y)
            if self.blit_pos == (self.grid_pos[0] * constants.TILE_SIZE, self.grid_pos[1] * constants.TILE_SIZE):
                self.animation.index = 0

    def do_animation(self, effect, attack_time_left, time_for_one_tile, display):
        if effect == "Damage":
            self.hurt_animation(attack_time_left, time_for_one_tile)
        elif effect in ["ATK+", "ATK-", "DEF+", "DEF-", "SPATK+", "SPATK-", "SPDEF+", "SPDEF-"]:
            self.stat_animation(effect, attack_time_left, time_for_one_tile, display)

    def hurt_animation(self, attack_time_left, time_for_one_tile):
        if self.hp == 0:
            upper_bound = 1.5
        else:
            upper_bound = 0.85
        if 0.15 < attack_time_left / time_for_one_tile <= upper_bound:
            self.animation_name = "Hurt"
        else:
            self.animation_name = "Walk"

    def attack_animation(self, m: move.Move, attack_time_left, time_for_one_tile):
        category = m.category
        if category == move.MoveCategory.PHYSICAL:
            self.animation_name = "Attack"
        if category == move.MoveCategory.SPECIAL:
            self.animation_name = "Attack"
        elif category == move.MoveCategory.STATUS:
            category = "Special"
            self.animation_name = "Charge"
        else:
            self.animation_name = "Idle"

        step_size = 1 / len(self.animation.frames)
        for i in range(len(self.animation.frames)):
            if step_size * i <= attack_time_left / time_for_one_tile < step_size * (i + 1):
                self.animation.index = i

        if category == move.MoveCategory.PHYSICAL:
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
    def possible_moves(self) -> list[move.Move]:
        return [self.move_set.moveset[i] for i in range(4) if self.move_set.moveset[i].pp and self.get_targets(self.move_set.moveset[i].effects[0])]

    def get_targets(self, effect: move.MoveEffect):
        targets = self.find_possible_targets(effect.target)
        targets = self.filter_out_of_range_targets(targets, effect.range_category, effect.cuts_corners)
        return targets

    def find_possible_targets(self, target_type):
        allies = self.dungeon.active_team
        enemies = self.dungeon.active_enemies
        if self.poke_type == "Enemy":
            allies, enemies = enemies, allies

        if target_type == "Self":
            return [self]
        elif target_type == "All":
            return self.dungeon.all_sprites
        elif target_type == "Allies":
            return allies
        elif target_type == "Enemies":
            return enemies

    def filter_out_of_range_targets(self, targets, move_range, cuts_corners):
        if move_range == 0:
            return [self]

        possible_directions = list(direction.Direction)
        if not cuts_corners:
            possible_directions = self.remove_corner_cutting_directions(possible_directions)

        if move_range == 1 or move_range == 2 or move_range == 10:  # Front
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
