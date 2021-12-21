from importsAndConstants import *

# Different dungeons should have different tile graphics.
# Tile Loading Function.
def tile_list(tile):  # Matches Tile image for all possibilities of tile arrangements.
    tiles = [tile]  # Stores the parameter in case there are no X's.
    indices = []
    for i in range(1, len(tile)):  # Stores indices of the X's in the string.
        if tile[i] == "X":
            indices.append(i)
    if len(indices) != 0:
        for d in range(2 ** (len(indices))):  # gets all possibilities of X values by counting in binary.
            binary_string = format(d, "#0" + str(len(indices) + 2) + "b")[2:]
            new_tile = list(tile)  # Makes the string a list.
            for x_index in range(len(indices)):
                new_tile[indices[x_index]] = binary_string[x_index]  # Replaces the X's with 1s or 0s
            new_tile = "".join(new_tile)  # Converts list back to string
            tiles.append(new_tile)
        tiles = tiles[1:]  # Removes the string with the X's.
    return tiles


# Pokemon Image Data
def pokemon_image_dict(poke_id):
    def load(current_directory, direction):
        direction_directory = os.path.join(current_directory, direction)
        images = [file for file in os.listdir(direction_directory) if file != "Thumbs.db"]
        return [scale(p.image.load(os.path.join(direction_directory, str(i) + ".png")).convert(), POKE_SIZE) for i in
                range(len(images))]

    full_dict = {}
    directory = os.path.join(os.getcwd(), "images", "Pokemon", poke_id)

    for image_type in [image_type for image_type in os.listdir(directory) if
                    image_type not in ["Thumbs.db", "Asleep"]]:  # ["Physical","Special","Motion","Hurt"]
        current_directory = os.path.join(directory, image_type)
        Dict = {(-1, -1): load(current_directory, "1"),
                (0, -1): load(current_directory, "2"),
                (1, -1): None,
                (-1, 0): load(current_directory, "4"),
                (0, 0): None,  ##############
                (1, 0): None,
                (-1, 1): load(current_directory, "7"),
                (0, 1): load(current_directory, "8"),
                (1, 1): None,
                }
        for key in Dict:
            if key[0] == -1:
                Dict[(1, key[1])] = [p.transform.flip(image, True, False) for image in
                                     Dict[key]]  # Inserts the flipped images into the dictionary
        Dict[(0, 0)] = [Dict[(0, 1)][0]]

        full_dict[image_type] = Dict
    full_dict["Asleep"] = {}
    full_dict["Asleep"]["0"] = load(os.path.join(directory, "Asleep"), "0")
    return full_dict


def stats_dict():
    Dict = {}
    directory = os.path.join(os.getcwd(), "images", "MoveAnimations", "Stat Change")
    stats = [stat for stat in os.listdir(directory) if stat != "Thumbs.db"]
    for stat in stats:
        Dict[stat] = {
            "+": [scale(p.image.load(os.path.join(directory, stat, "001", image)).convert_alpha(), TILE_SIZE) for image in
                  os.listdir(os.path.join(directory, stat, "001")) if image != "Thumbs.db"][::-1],
            "-": [scale(p.image.load(os.path.join(directory, stat, "000", image)).convert_alpha(), TILE_SIZE) for image in
                  os.listdir(os.path.join(directory, stat, "000")) if image != "Thumbs.db"][::-1]
            }
    return Dict


stats_animation_dict = stats_dict()


dungeons = [os.path.join(os.getcwd(), "images", "Dungeons", file) for file in
            os.listdir(os.path.join(os.getcwd(), "images", "Dungeons")) if file != "Thumbs.db"]
dungeon_dict = {}

for dungeon in dungeons:
    tile_type = [tile_type for tile_type in os.listdir(os.path.join(dungeon)) if tile_type != "Thumbs.db"]
    dungeon_dict[dungeon] = {}
    for i in range(len(tile_type)):
        tiles = [tile for tile in os.listdir(os.path.join(dungeon, tile_type[i])) if tile.endswith(".png")]
        tile_data = {}
        for tile in tiles:
            img = scale(p.image.load(os.path.join(dungeon, tile_type[i], tile)).convert(), TILE_SIZE)
            tile_data[tile] = tile_list(tile) + [img]
        dungeon_dict[dungeon][tile_type[i]] = tile_data
