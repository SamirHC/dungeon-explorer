from map import *
from PokemonStructure import *
from LoadImages import *
from textbox import *
import configparser


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



def load_move_object(name):
    return Move(name,
                power=[int(x) for x in move_dict[name]["power"].split(",")],
                accuracy=[int(x) for x in move_dict[name]["accuracy"].split(",")],
                critical=int(move_dict[name]["critical"]),
                pp=int(move_dict[name]["pp"]),
                type=move_dict[name]["type"],
                category=move_dict[name]["category"],
                cuts_corners=int(move_dict[name]["cutscorners"]),
                target_type=move_dict[name]["targettype"].split(","),
                ranges=move_dict[name]["ranges"].split(","),
                effects=move_dict[name]["effects"].split(",")
                )


# Dungeons
def load_dungeon_data():
    dungeon_data_dict = {}
    with open(os.path.join(os.getcwd(), "GameData", "DungeonData.txt")) as f:
        f = f.readlines()
    f = [line[:-1].split(",") for line in f][1:]
    for dungeon in f:
        temp_dict = {}
        name = dungeon[0]
        temp_dict["MaxPath"] = int(dungeon[1])
        temp_dict["MinRoom"] = int(dungeon[2])
        temp_dict["MaxRoom"] = int(dungeon[3])
        temp_dict["MinDim"] = int(dungeon[4])
        temp_dict["MaxDim"] = int(dungeon[5])
        dungeon_data_dict[name] = temp_dict
    return dungeon_data_dict

dungeon_data_dict = load_dungeon_data()

def load_dungeon_object(name):
    return Map(max_path=dungeon_data_dict[name]["MaxPath"],
               min_room=dungeon_data_dict[name]["MinRoom"],
               max_room=dungeon_data_dict[name]["MaxRoom"],
               min_dim=dungeon_data_dict[name]["MinDim"],
               max_dim=dungeon_data_dict[name]["MaxDim"],
               tile_dict=dungeon_dict[os.path.join(os.getcwd(), "images", "Dungeons", name)],
               map_image=None,
               path_coords=[],
               room_coords=[],
               water_coords=[],
               stairs_coords=["Down"],
               trap_coords=[],
               floor=[[" " for x in range(COLS)] for x in range(ROWS)],
               specific_floor_tile_images=[["" for x in range(COLS)] for x in range(ROWS)]
               )


# Pokemon
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
        level = specific_pokemon_data["LVL"]
        xp = specific_pokemon_data["XP"]
        hp = pokemon_base_stats_dict[poke_id]["HP"] + specific_pokemon_data["HP"]
        ATK = pokemon_base_stats_dict[poke_id]["ATK"] + specific_pokemon_data["ATK"]
        DEF = pokemon_base_stats_dict[poke_id]["DEF"] + specific_pokemon_data["DEF"]
        SPATK = pokemon_base_stats_dict[poke_id]["SPATK"] + specific_pokemon_data["SPATK"]
        SPDEF = pokemon_base_stats_dict[poke_id]["SPDEF"] + specific_pokemon_data["SPDEF"]
        move_set = []
        for i in range(1, 6):
            current_move = user_specific_pokemon_dict[poke_id]["Move" + str(i)]
            move_set.append(load_move_object(current_move))

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
            current_move = dungeon_specific_pokemon_dict[dungeon][poke_id]["Move" + str(i)]
            move_set.append(load_move_object(current_move))
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
    StatusDict = {"HP": hp,
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
                   current_image=image_dict["Motion"][(0, 1)][0],
                   poke_type=poke_type,
                   battle_info=PokemonBattleInfo(poke_id,
                                                name=pokemon_base_stats_dict[poke_id]["Name"],
                                                level=level,
                                                xp=xp,
                                                type1=pokemon_base_stats_dict[poke_id]["Type1"],
                                                type2=pokemon_base_stats_dict[poke_id]["Type2"],
                                                base=base_dict,
                                                status=StatusDict,
                                                move_set=move_set
                                                )
                   )
