from map import *
from PokemonStructure import *
from LoadImages import *
from textbox import *
from move import Move
from pokemon_battle_info import PokemonBattleInfo

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
                   current_image=image_dict["Motion"][(0, 1)][0],
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
