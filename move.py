import os
import configparser

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

class Move:
    def __init__(self, name: str):
        self.name = name
        # Single
        self.power = [int(x) for x in move_dict[name]["power"].split(",")]
        self.accuracy = [int(x) for x in move_dict[name]["accuracy"].split(",")]
        self.critical = int(move_dict[name]["critical"])
        self.pp = int(move_dict[name]["pp"])
        self.type = move_dict[name]["type"]
        self.category = move_dict[name]["category"]  # ["ATK","SPATK"]
        self.cuts_corners = int(move_dict[name]["cutscorners"])  # 1/0 [True/False]
        # Multi
        self.target_type = move_dict[name]["targettype"].split(",")  # ["Self","Allies","Enemies","All"]
        self.ranges = move_dict[name]["ranges"].split(",")
        self.effects = move_dict[name]["effects"].split(",")  # ["Damage","Heal","ATK+","DEF+","SPATK+","SPDEF+","ATK-","DEF-","SPATK-","SPDEF-"...]

    def empty_pp(self):
        self.pp = 0