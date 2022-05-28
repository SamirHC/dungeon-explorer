import dataclasses
import enum
import os
import xml.etree.ElementTree as ET

from dungeon_explorer.dungeon import damage_chart


class MoveCategory(enum.Enum):
    PHYSICAL = "Physical"
    SPECIAL = "Special"
    OTHER = "Other"


class MoveRange(enum.Enum):
    ADJACENT_POKEMON = "Adjacent Pokémon"
    ALL_ENEMIES_IN_THE_ROOM = "All enemies in the room"
    ALL_ENEMIES_ON_THE_FLOOR = "All enemies on the floor"
    ALL_IN_THE_ROOM_EXCEPT_USER = "All in the room except user"
    ALL_POKEMON_IN_THE_ROOM = "All Pokémon in the room"
    ALL_POKEMON_ON_THE_FLOOR = "All Pokémon on the floor"
    ALL_TEAM_MEMBERS_IN_THE_ROOM = "All team members in the room"
    ENEMIES_WITHIN_1_TILE_RANGE = "Enemies within 1-tile range"
    ENEMY_IN_FRONT = "Enemy in front"
    ENEMY_IN_FRONT_CUTS_CORNERS = "Enemy in front, cuts corners"
    ENEMY_UP_TO_2_TILES_AWAY = "Enemy up to 2 tiles away"
    FACING_POKEMON = "Facing Pokémon"
    FACING_POKEMON_CUTS_CORNERS = "Facing Pokémon, cuts corners"
    FACING_TILE_AND_2_FLANKING_TILES = "Facing tile and 2 flanking tiles"
    FLOOR = "Floor"
    ITEM = "Item"
    LINE_OF_SIGHT = "Line of sight"
    ONLY_THE_ALLIES_IN_THE_ROOM = "Only the allies in the room"
    POKEMON_WITHIN_1_TILE_RANGE = "Pokémon within 1-tile range"
    POKEMON_WITHIN_2_TILE_RANGE = "Pokémon within 2-tile range"
    SPECIAL = "Special"
    TEAM_MEMBERS_ON_THE_FLOOR = "Team members on the floor"
    USER = "User"
    WALL = "Wall"


@dataclasses.dataclass(frozen=True)
class Move:
    move_id: int
    name: str
    description: str
    type: damage_chart.Type
    category: MoveCategory
    pp: int
    accuracy: int
    critical: int
    power: int
    animation: int
    chained_hits: int
    move_range: MoveRange
    weight: int
    activation_condition: str
    ginseng: bool
    magic_coat: bool
    snatch: bool
    muzzled: bool
    taunt: bool
    frozen: bool
    effect: int


class MoveDatabase:
    def __init__(self):
        self.base_dir = os.path.join("data", "gamedata", "moves")
        self.loaded: dict[int, Move] = {}

    def __getitem__(self, move_id: int) -> Move:
        if move_id not in self.loaded:
            self.load(move_id)
        return self.loaded[move_id]

    def load(self, move_id: int):
        if move_id in self.loaded:
            return
        
        filename = os.path.join(self.base_dir, f"{move_id}.xml")
        root = ET.parse(filename).getroot()

        name = root.find("Name").text
        description = root.find("Description").text
        type = damage_chart.Type(int(root.find("Type").text))
        category = MoveCategory(root.find("Category").text)

        stats = root.find("Stats")
        pp = int(stats.find("PP").text)
        power = int(stats.find("Power").text)
        accuracy = int(stats.find("Accuracy").text)
        critical = int(stats.find("Critical").text)
        
        animation = int(root.find("Animation").text)
        chained_hits = int(root.find("ChainedHits").text)
        move_range = MoveRange(root.find("Range").text)

        flags = root.find("Flags")
        ginseng = bool(int(flags.find("Ginseng").text))
        magic_coat = bool(int(flags.find("MagicCoat").text))
        snatch = bool(int(flags.find("Snatch").text))
        muzzled = bool(int(flags.find("Muzzled").text))
        taunt = bool(int(flags.find("Taunt").text))
        frozen = bool(int(flags.find("Frozen").text))
        effect = int(flags.find("Effect").text)

        ai = root.find("AI")
        weight = int(ai.find("Weight").text)
        activation_condition = ai.find("ActivationCondition").text

        self.loaded[move_id] = Move(
            move_id,
            name,
            description,
            type,
            category,
            pp,
            accuracy,
            critical,
            power,
            animation,
            chained_hits,
            move_range,
            weight,
            activation_condition,
            ginseng,
            magic_coat,
            snatch,
            muzzled,
            taunt,
            frozen,
            effect
        )


db = MoveDatabase()
REGULAR_ATTACK = db[0]
STRUGGLE = db[352]