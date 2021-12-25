from dungeon_map import DungeonMap
import os

class Dungeon:

    def __init__(self, dungeon_id):
        self.dungeon_id = dungeon_id
        self.dungeon_map = DungeonMap(dungeon_id)

    
