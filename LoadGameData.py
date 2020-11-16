from DungeonGeneration import *
from PokemonStructure import *
from LoadImages import *
from TextBox import *
import configparser
import time


# Moves
def LoadMoveData():
    MoveDict = {}
    directory = os.path.join(os.getcwd(), "GameData", "Moves")
    config = configparser.RawConfigParser()
    for Move in os.listdir(directory):
        TempDict = {}
        MoveDir = os.path.join(directory, Move, "moveData.cfg")
        config.read(MoveDir)
        section = config.sections()[0]
        options = config.options(section)
        for option in options:
            TempDict[option] = config.get(section, option)
        MoveDict[Move] = TempDict
    return MoveDict

MoveDict = LoadMoveData()



def LoadMoveObject(NAME):
    return Move(Name=NAME,
                Power=[int(x) for x in MoveDict[NAME]["power"].split(",")],
                Accuracy=[int(x) for x in MoveDict[NAME]["accuracy"].split(",")],
                Critical=int(MoveDict[NAME]["critical"]),
                PP=int(MoveDict[NAME]["pp"]),
                Type=MoveDict[NAME]["type"],
                Category=MoveDict[NAME]["category"],
                CutsCorners=int(MoveDict[NAME]["cutscorners"]),
                TargetType=MoveDict[NAME]["targettype"].split(","),
                Ranges=MoveDict[NAME]["ranges"].split(","),
                Effects=MoveDict[NAME]["effects"].split(",")
                )


# Dungeons
def LoadDungeonData():
    DungeonDataDict = {}
    with open(os.path.join(os.getcwd(), "GameData", "DungeonData.txt")) as F:
        F = F.readlines()
    F = [line[:-1].split(",") for line in F][1:]
    for Dungeon in F:
        TempDict = {}
        Name = Dungeon[0]
        TempDict["MaxPath"] = int(Dungeon[1])
        TempDict["MinRoom"] = int(Dungeon[2])
        TempDict["MaxRoom"] = int(Dungeon[3])
        TempDict["MinDim"] = int(Dungeon[4])
        TempDict["MaxDim"] = int(Dungeon[5])
        DungeonDataDict[Name] = TempDict
    return DungeonDataDict

DungeonDataDict = LoadDungeonData()

def LoadDungeonObject(NAME):
    return Map(MaxPath=DungeonDataDict[NAME]["MaxPath"],
               MinRoom=DungeonDataDict[NAME]["MinRoom"],
               MaxRoom=DungeonDataDict[NAME]["MaxRoom"],
               MinDim=DungeonDataDict[NAME]["MinDim"],
               MaxDim=DungeonDataDict[NAME]["MaxDim"],
               TileDict=DungeonDict[os.path.join(os.getcwd(), "images", "Dungeons", NAME)],
               MapImage=None,
               PathCoords=[],
               RoomCoords=[],
               WaterCoords=[],
               StairsCoords=["Down"],
               TrapCoords=[],
               Floor=[[" " for x in range(MAP_X)] for x in range(MAP_Y)],
               SpecificFloorTileImages=[["" for x in range(MAP_X)] for x in range(MAP_Y)]
               )


# Pokemon
def LoadBasePokemonData():
    PokemonBaseStatsDict = {}
    with open(os.path.join(os.getcwd(), "GameData", "PokemonBaseStats.txt")) as F:
        F = F.readlines()
    F = [line[:-1].split(",") for line in F][1:]
    for Poke in F:
        try:
            TempDict = {}
            ID = Poke[0]
            TempDict["Name"] = Poke[1]
            TempDict["HP"] = int(Poke[2])
            TempDict["ATK"] = int(Poke[3])
            TempDict["DEF"] = int(Poke[4])
            TempDict["SPATK"] = int(Poke[5])
            TempDict["SPDEF"] = int(Poke[6])
            TempDict["Type1"] = Poke[7]
            TempDict["Type2"] = Poke[8]
            PokemonBaseStatsDict[ID] = TempDict
        except:
            pass
    return PokemonBaseStatsDict


PokemonBaseStatsDict = LoadBasePokemonData()


def LoadUserSpecificPokemonData():
    PokemonSpecificDict = {}
    d = os.path.join(os.getcwd(), "UserData", "UserTeamData.txt")
    with open(d) as F:
        F = F.readlines()
    F = [line[:-1].split(",") for line in F][1:]
    for Poke in F:
        TempDict = {}
        ID = Poke[0]
        TempDict["LVL"] = int(Poke[1])
        TempDict["XP"] = int(Poke[2])
        TempDict["HP"] = int(Poke[3])
        TempDict["ATK"] = int(Poke[4])
        TempDict["DEF"] = int(Poke[5])
        TempDict["SPATK"] = int(Poke[6])
        TempDict["SPDEF"] = int(Poke[7])
        TempDict["Move1"] = Poke[8]
        TempDict["Move2"] = Poke[9]
        TempDict["Move3"] = Poke[10]
        TempDict["Move4"] = Poke[11]
        TempDict["Move5"] = "Regular Attack"
        PokemonSpecificDict[ID] = TempDict
    return PokemonSpecificDict


UserSpecificPokemonDict = LoadUserSpecificPokemonData()


def LoadDungeonSpecificPokemonData():
    Dict = {}
    d = [Dungeon for Dungeon in os.listdir(os.path.join(os.getcwd(), "GameData", "Dungeons")) if Dungeon != "Thumbs.db"]
    for Dungeon in d:
        DungeonDict = {}
        file = os.path.join(os.getcwd(), "GameData", "Dungeons", Dungeon, "PokemonData.txt")
        with open(file) as F:
            F = F.readlines()
        F = [line[:-1].split(",") for line in F][1:]
        for Poke in F:
            TempDict = {}
            ID = Poke[0]
            TempDict["LVL"] = int(Poke[1])
            TempDict["XP"] = int(Poke[2])
            TempDict["HP"] = int(Poke[3])
            TempDict["ATK"] = int(Poke[4])
            TempDict["DEF"] = int(Poke[5])
            TempDict["SPATK"] = int(Poke[6])
            TempDict["SPDEF"] = int(Poke[7])
            TempDict["Move1"] = Poke[8]
            TempDict["Move2"] = Poke[9]
            TempDict["Move3"] = Poke[10]
            TempDict["Move4"] = Poke[11]
            TempDict["Move5"] = "Regular Attack"
            DungeonDict[ID] = TempDict
        Dict[Dungeon] = DungeonDict
    return Dict


DungeonSpecificPokemonDict = LoadDungeonSpecificPokemonData()


def LoadPokemonObject(ID, pokeType, dungeon=None):
    if pokeType == "User" or pokeType == "Team":
        SpecificPokemonData = UserSpecificPokemonDict[ID]
        LVL = SpecificPokemonData["LVL"]
        XP = SpecificPokemonData["XP"]
        HP = PokemonBaseStatsDict[ID]["HP"] + SpecificPokemonData["HP"]
        ATK = PokemonBaseStatsDict[ID]["ATK"] + SpecificPokemonData["ATK"]
        DEF = PokemonBaseStatsDict[ID]["DEF"] + SpecificPokemonData["DEF"]
        SPATK = PokemonBaseStatsDict[ID]["SPATK"] + SpecificPokemonData["SPATK"]
        SPDEF = PokemonBaseStatsDict[ID]["SPDEF"] + SpecificPokemonData["SPDEF"]
        MoveSet = []
        for i in range(1, 6):
            currentMove = UserSpecificPokemonDict[ID]["Move" + str(i)]
            MoveSet.append(LoadMoveObject(currentMove))

    elif pokeType == "Enemy" and dungeon:
        SpecificPokemonData = DungeonSpecificPokemonDict[dungeon][ID]

        LVL = SpecificPokemonData["LVL"]
        XP = SpecificPokemonData["XP"]
        HP = PokemonBaseStatsDict[ID]["HP"] + SpecificPokemonData["HP"]
        ATK = PokemonBaseStatsDict[ID]["ATK"] + SpecificPokemonData["ATK"]
        DEF = PokemonBaseStatsDict[ID]["DEF"] + SpecificPokemonData["DEF"]
        SPATK = PokemonBaseStatsDict[ID]["SPATK"] + SpecificPokemonData["SPATK"]
        SPDEF = PokemonBaseStatsDict[ID]["SPDEF"] + SpecificPokemonData["SPDEF"]
        MoveSet = []
        for i in range(1, 6):
            currentMove = DungeonSpecificPokemonDict[dungeon][ID]["Move" + str(i)]
            MoveSet.append(LoadMoveObject(currentMove))
    imageDict = PokemonImgDict(ID)
    BaseDict = {"HP": HP,
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
    StatusDict = {"HP": HP,
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
    return Pokemon(imageDict=imageDict,
                   currentImg=imageDict["Motion"][(0, 1)][0],
                   pokeType=pokeType,
                   BattleInfo=PokemonBattleInfo(ID,
                                                Name=PokemonBaseStatsDict[ID]["Name"],
                                                LVL=LVL,
                                                XP=XP,
                                                Type1=PokemonBaseStatsDict[ID]["Type1"],
                                                Type2=PokemonBaseStatsDict[ID]["Type2"],
                                                Base=BaseDict,
                                                Status=StatusDict,
                                                MoveSet=MoveSet
                                                )
                   )
