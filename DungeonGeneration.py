from ImportsAndConstants import *


class Map:
    COLS = 65
    ROWS = 40

    def __init__(self,
                 MaxPath,
                 MinRoom, MaxRoom,
                 MinDim, MaxDim,
                 TileDict,
                 MapImage=None,
                 PathCoords=None, RoomCoords=None, WaterCoords=None, StairsCoords=None, TrapCoords=None,
                 Floor=None, SpecificFloorTileImages=None
                 ):
        self.Floor = Floor  # Map Tile data as a list
        self.MaxPath = MaxPath  # Most number of distinct paths
        self.MinRoom = MinRoom  # Min number of rooms
        self.MaxRoom = MaxRoom  # Max ^
        self.MinDim = MinDim  # Min dimensions of a room
        self.MaxDim = MaxDim  # Max ^
        self.PathCoords = PathCoords  # Coordinates of all PathTiles
        self.RoomCoords = RoomCoords  # ^ RoomTiles
        self.WaterCoords = WaterCoords
        self.StairsCoords = StairsCoords
        self.TrapCoords = TrapCoords
        self.MapImage = MapImage
        self.TileDict = TileDict
        self.SpecificFloorTileImages = SpecificFloorTileImages

    #####################################################################################################################################################
    def SpreadCalc(self):
        Total_x = Total_y = 0
        Max_x = Min_x = self.PathCoords[0][0]
        Max_y = Min_y = self.PathCoords[0][1]

        for coord in self.PathCoords:
            x, y = coord[0], coord[1]
            if x > Max_x:  # Used in range calc
                Max_x = x
            if x < Min_x:
                Min_x = x
            if y > Max_y:
                Max_y = y
            if y < Min_y:
                Min_y = y
            Total_x += x  # Used in COM calc
            Total_y += y  # "
            if y < Map.ROWS - 1 and x < Map.COLS - 1:
                if self.Floor[y + 1][x] == self.Floor[y][x + 1] == self.Floor[y + 1][x + 1] == "P":
                    return (0, 0), 0, 0  # Path cannot be naturally wider than 1 tile.

        M = len(self.PathCoords)  # Total mass of system
        xrange = Max_x - Min_x
        yrange = Max_y - Min_y
        CoM = (Total_x / M, Total_y / M)
        return CoM, xrange, yrange

    def CheckValidPaths(self):
        Data = self.SpreadCalc()
        if abs(Data[0][0] - Map.COLS / 2) < 0.2 * Map.COLS and abs(Data[0][1] - Map.ROWS / 2) < 0.2 * Map.COLS and Map.COLS * 0.6 < \
                Data[1] < COLS and ROWS * 0.6 < Data[2] < ROWS:
            return True  # Valid for ^
        else:
            return False

    def InsertPaths(self):
        pos = (randint(2, COLS - 3), randint(2, ROWS - 3))  # Starting position of path generation
        for y in range(self.MaxPath):  # generate paths
            Direction = randint(0, 3)  # 0 = Up, 1 = Down, 2 = Left, 3 = Right
            if Direction == 0:  # Up
                a = randint(2, pos[1])
                for y in range(a, pos[1] + 1):
                    self.Floor[y][pos[0]] = "P"
                    self.PathCoords.append((pos[0], y))
                pos = (pos[0], a)
            elif Direction == 1:  # Down
                a = randint(pos[1], ROWS - 3)
                for y in range(pos[1], a + 1):
                    self.Floor[y][pos[0]] = "P"
                    self.PathCoords.append((pos[0], y))
                pos = (pos[0], a)
            elif Direction == 2:  # Left
                a = randint(2, pos[0])
                for x in range(a, pos[0] + 1):
                    self.Floor[pos[1]][x] = "P"
                    self.PathCoords.append((x, pos[1]))
                pos = (a, pos[1])
            elif Direction == 3:  # Right
                a = randint(pos[0], COLS - 3)
                for x in range(pos[0], a + 1):
                    self.Floor[pos[1]][x] = "P"
                    self.PathCoords.append((x, pos[1]))
                pos = (a, pos[1])

        self.PathCoords = remove_duplicates(self.PathCoords)

    def InsertWater(self):
        r = randint(self.MinDim, self.MaxDim) // 2
        pos = (randint(2 + r, COLS - 2 - self.MinDim - r),
               randint(2 + r, ROWS - 2 - self.MinDim - r))  # topleft corner of room coordinate
        for x in range(-r, r + 1):
            for y in range(-r, r + 1):
                distance = (y ** 2 + x ** 2) ** 0.5
                if self.Floor[pos[1] + y][pos[0] + x] == " " and distance <= r:
                    self.Floor[pos[1] + y][pos[0] + x] = "F"  # Fill area with Water Tile
                    self.WaterCoords.append([pos[0] + x, pos[1] + y])

    def CheckValidRoom(self, Pos, Dim):
        x, y = Pos[0], Pos[1]
        w, h = Dim[0], Dim[1]
        if x + w >= COLS - 1 or y + h >= ROWS - 1:  # Should be within map boundaries
            return False
        else:
            pass

        Area = [self.Floor[y + i - 1][x - 1: x + w + 1] for i in
                range(h + 2)]  # Gets the tile info of the area where the room would be placed (including surroundings)
        Area = sum(Area, [])

        UpLeftCorner = [Area[0]]
        UpRightCorner = [Area[w + 1]]
        DownLeftCorner = [Area[-w - 2]]
        DownRightCorner = [Area[-1]]
        UpEdge = Area[1:w + 1]
        DownEdge = Area[-w - 1:-1][::-1]
        LeftEdge = [Area[i] for i in range(1, (w + 2) * (h + 1)) if i % (w + 2) == 0][::-1]
        RightEdge = [Area[i] for i in range(w + 2, (w + 2) * (h + 1)) if i % (w + 2) == (w + 1)]

        Border = UpLeftCorner + UpEdge + UpRightCorner + RightEdge + DownRightCorner + DownEdge + DownLeftCorner + LeftEdge + UpLeftCorner
        del Area[-w - 2]
        del Area[-1]  # Removes corners
        del Area[w + 1]
        del Area[0]

        valid = False
        if "P" in Area:
            valid = True
        if "R" in Area:
            valid = False
        for i in range(len(Border) - 1):
            if Border[i] == Border[i + 1] == "P":
                valid = False
        return valid

    def InsertRooms(self):
        while True:
            pos = (randint(2, COLS - 2 - self.MinDim),
                   randint(2, ROWS - 2 - self.MinDim))  # topleft corner of room coordinate
            dim = (randint(self.MinDim, self.MaxDim), randint(self.MinDim, self.MaxDim))
            if self.CheckValidRoom(pos, dim):
                break
        Room = []
        for x in range(dim[0]):
            for y in range(dim[1]):
                self.Floor[pos[1] + y][pos[0] + x] = "R"  # Fill area with Room Tile
                Room.append([pos[0] + x, pos[1] + y])
        self.RoomCoords.append(Room)

    def InsertMisc(self):
        RoomTiles = []
        Type = self.StairsCoords[0]
        StairsImg = scale(
            p.image.load(os.path.join(os.getcwd(), "images", "Stairs", "Stairs" + Type + ".png")).convert(), TILE_SIZE)
        TrapImg = scale(p.image.load(os.path.join(os.getcwd(), "images", "Traps", "WonderTile.png")).convert(),
                        TILE_SIZE)

        for coord in sum(self.RoomCoords, []):
            x, y = coord[0], coord[1]
            if self.Floor[y + 1][x] != "P" and self.Floor[y - 1][x] != "P" and self.Floor[y][x - 1] != "P" and \
                    self.Floor[y][x + 1] != "P":
                RoomTiles.append([x, y])  # Cannot be next to a path and must be in a room
        i = randint(0, len(RoomTiles) - 1)
        x, y = RoomTiles[i][0], RoomTiles[i][1]  # pick a random suitable room tile
        self.StairsCoords.append([x, y])  # Insert Stairs
        del RoomTiles[i]

        self.MapImage.blit(StairsImg, (x * TILE_SIZE, y * TILE_SIZE))
        for t in range(TRAPS_PER_FLOOR):  # Insert Traps
            i = randint(0, len(RoomTiles) - 1)
            x, y = RoomTiles[i][0], RoomTiles[i][1]
            self.TrapCoords.append([x, y])
            self.MapImage.blit(TrapImg, (x * TILE_SIZE, y * TILE_SIZE))
            del RoomTiles[i]

    def FindSpecificFloorTiles(self):
        for y in range(1, len(self.Floor) - 1):
            for x in range(1, len(self.Floor[y]) - 1):  # Iterate through every non-border tile
                Legend = ""  # Image File binary name
                Tile = self.Floor[y][x]  # Determine the type of tile
                for j in range(-1, 2):
                    for i in range(-1, 2):  # Iterate through every surrounding tile
                        if self.Floor[y + j][x + i] == Tile:
                            Legend = Legend + "1"
                        else:
                            Legend = Legend + "0"
                if Tile in ["P", "R"]:  # Ground tiles are used for Paths and Rooms
                    Tile = "G"
                elif Tile == " ":
                    Tile = "W"
                elif Tile == "F":
                    Tile = "F"
                self.SpecificFloorTileImages[y][
                    x] = Tile + Legend + ".png"  # Stores Tile names in this list similar to self.Floor, but specific to graphics

    def InsertBorders(self):  # Surround map with empty/wall tile
        for x in range(COLS):  # Top and Bottom borders
            self.SpecificFloorTileImages[0][x] = self.SpecificFloorTileImages[ROWS - 1][x] = "B111111111.png"
        for y in range(ROWS):  # Left and Right bornders
            self.SpecificFloorTileImages[y][0] = self.SpecificFloorTileImages[y][COLS - 1] = "B111111111.png"

    def DrawMap(self):  # Blits tiles onto map.
        mapSurface = p.Surface((TILE_SIZE * len(self.Floor[0]), TILE_SIZE * len(self.Floor)))
        self.InsertBorders()
        for y in range(len(self.Floor)):
            for x in range(len(self.Floor[y])):
                Tile = self.SpecificFloorTileImages[y][x]
                possibleImages = []
                for TileType in self.TileDict:
                    for GenTile in self.TileDict[TileType]:
                        if Tile in self.TileDict[TileType][GenTile]:
                            possibleImages.append(self.TileDict[TileType][GenTile][-1])
                img = possibleImages[randint(0, len(possibleImages) - 1)]
                mapSurface.blit(img, (TILE_SIZE * x, TILE_SIZE * y))

        self.MapImage = mapSurface

    def BuildMap(self):
        valid = False
        while not valid:
            self.PathCoords = []  # empty each time it is invalid
            self.Floor = [[" " for x in range(COLS)] for x in range(ROWS)]  # Generates empty floor layout
            self.InsertPaths()  # Inserts the paths onto the floor
            valid = self.CheckValidPaths()
        for n in range(randint(self.MinRoom, self.MaxRoom)):
            self.InsertWater()
        for n in range(randint(self.MinRoom, self.MaxRoom)):
            self.InsertRooms()  # Inserts the rooms onto the floor
        self.FindSpecificFloorTiles()
        self.DrawMap()
        self.InsertMisc()  # Inserts stairs and traps
        return Map(self.MaxPath, self.MinRoom, self.MaxRoom, self.MinDim, self.MaxDim, self.TileDict, self.MapImage,
                   self.PathCoords, self.RoomCoords, self.WaterCoords, self.StairsCoords, self.TrapCoords, self.Floor,
                   self.SpecificFloorTileImages)

    def DisplayMap(self, pos):
        display.blit(self.MapImage, pos)
