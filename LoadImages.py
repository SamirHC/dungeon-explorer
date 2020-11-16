from ImportsAndConstants import *
import time

# Different dungeons should have different tile graphics.
# Tile Loading Function.
def TileList(TILE):  # Matches Tile image for all possibilities of tile arrangements.
    tileList = [TILE]  # Stores the parameter in case there are no X's.
    indices = []
    for i in range(1, len(TILE)):  # Stores indices of the X's in the string.
        if TILE[i] == "X":
            indices.append(i)
    if len(indices) != 0:
        for d in range(2 ** (len(indices))):  # gets all possibilities of X values by counting in binary.
            binaryString = format(d, "#0" + str(len(indices) + 2) + "b")[2:]
            NewTile = list(TILE)  # Makes the string a list.
            for xIndex in range(len(indices)):
                NewTile[indices[xIndex]] = binaryString[xIndex]  # Replaces the X's with 1s or 0s
            NewTile = "".join(NewTile)  # Converts list back to string
            tileList.append(NewTile)
        tileList = tileList[1:]  # Removes the string with the X's.
    return tileList


# Pokemon Image Data
def PokemonImgDict(ID):
    def Load(currentDir, direction):
        directionDir = os.path.join(currentDir, direction)
        listOfImages = [file for file in os.listdir(directionDir) if file != "Thumbs.db"]
        return [Scale(p.image.load(os.path.join(directionDir, str(i) + ".png")).convert(), POKESIZE) for i in
                range(len(listOfImages))]

    FullDict = {}
    directory = os.path.join(os.getcwd(), "images", "Pokemon", ID)

    for imgType in [imgType for imgType in os.listdir(directory) if
                    imgType not in ["Thumbs.db", "Asleep"]]:  # ["Physical","Special","Motion","Hurt"]
        currentDir = os.path.join(directory, imgType)
        Dict = {(-1, -1): Load(currentDir, "1"),
                (0, -1): Load(currentDir, "2"),
                (1, -1): None,
                (-1, 0): Load(currentDir, "4"),
                (0, 0): None,  ##############
                (1, 0): None,
                (-1, 1): Load(currentDir, "7"),
                (0, 1): Load(currentDir, "8"),
                (1, 1): None,
                }
        for key in Dict:
            if key[0] == -1:
                Dict[(1, key[1])] = [p.transform.flip(img, True, False) for img in
                                     Dict[key]]  # Inserts the flipped images into the dictionary
        Dict[(0, 0)] = [Dict[(0, 1)][0]]

        FullDict[imgType] = Dict
    FullDict["Asleep"] = {}
    FullDict["Asleep"]["0"] = Load(os.path.join(directory, "Asleep"), "0")
    return FullDict


def StatsDict():
    Dict = {}
    directory = os.path.join(os.getcwd(), "images", "MoveAnimations", "Stat Change")
    Stats = [stat for stat in os.listdir(directory) if stat != "Thumbs.db"]
    for stat in Stats:
        Dict[stat] = {
            "+": [Scale(p.image.load(os.path.join(directory, stat, "001", img)).convert_alpha(), TILESIZE) for img in
                  os.listdir(os.path.join(directory, stat, "001")) if img != "Thumbs.db"][::-1],
            "-": [Scale(p.image.load(os.path.join(directory, stat, "000", img)).convert_alpha(), TILESIZE) for img in
                  os.listdir(os.path.join(directory, stat, "000")) if img != "Thumbs.db"][::-1]
            }
    return Dict


StatsAnimDict = StatsDict()


Dungeons = [os.path.join(os.getcwd(), "images", "Dungeons", File) for File in
            os.listdir(os.path.join(os.getcwd(), "images", "Dungeons")) if File != "Thumbs.db"]
DungeonDict = {}

for Dungeon in Dungeons:
    TileType = [TileType for TileType in os.listdir(os.path.join(Dungeon)) if TileType != "Thumbs.db"]
    DungeonDict[Dungeon] = {}
    for i in range(len(TileType)):
        Tiles = [Tile for Tile in os.listdir(os.path.join(Dungeon, TileType[i])) if Tile.endswith(".png")]
        TileData = {}
        for Tile in Tiles:
            img = Scale(p.image.load(os.path.join(Dungeon, TileType[i], Tile)).convert(), TILESIZE)
            TileData[Tile] = TileList(Tile) + [img]
        DungeonDict[Dungeon][TileType[i]] = TileData
