import os
import configparser

class Move:
    MOVE_DIRECTORY = os.path.join(os.getcwd(), "GameData", "Moves")

    def __init__(self, name: str):
        self.name = name
        self.load_move_data()
        # Single
        
    def load_move_data(self):
        config = configparser.RawConfigParser()
        data = os.path.join(Move.MOVE_DIRECTORY, self.name, "moveData.cfg")
        config.read(data)
        section = config.sections()[0]
        self.power = [int(x) for x in config.get(section, "power").split(",")]
        self.accuracy = [int(x) for x in config.get(section, "accuracy").split(",")]
        self.critical = int(config.get(section, "critical"))
        self.pp = int(config.get(section, "pp"))
        self.type = config.get(section, "type")
        self.category = config.get(section, "category")  # ["ATK","SPATK"]
        self.cuts_corners = int(config.get(section, "cutscorners"))  # 1/0 [True/False]
        # Multi
        self.target_type = config.get(section, "targettype").split(",")  # ["Self","Allies","Enemies","All"]
        self.ranges = config.get(section, "ranges").split(",")
        self.effects = config.get(section, "effects").split(",")  # ["Damage","Heal","ATK+","DEF+","SPATK+","SPDEF+","ATK-","DEF-","SPATK-","SPDEF-"...]

    def empty_pp(self):
        self.pp = 0