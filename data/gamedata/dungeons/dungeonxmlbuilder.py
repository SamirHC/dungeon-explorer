import os
import xml.etree.ElementTree as ET


def buildtree():
    root = ET.Element("Move")
    name = ET.SubElement(root, "Name")
    name.text = "Test Dungeon"
    is_below = ET.SubElement(root, "IsBelow")
    is_below.text = "1"
    exp_enabled = ET.SubElement(root, "ExpEnabled")
    exp_enabled.text = "0"
    recruiting_enabled = ET.SubElement(root, "RecruitingEnabled")
    recruiting_enabled.text = "0"
    level_reset = ET.SubElement(root, "LevelReset")
    level_reset.text = "0"
    money_reset = ET.SubElement(root, "MoneyReset")
    money_reset.text = "0"
    iq_enabled = ET.SubElement(root, "IqEnabled")
    iq_enabled.text = "0"
    reveal_traps = ET.SubElement(root, "RevealTraps")
    reveal_traps.text = "0"
    enemies_drop_boxes = ET.SubElement(root, "EnemiesDropBoxes")
    enemies_drop_boxes.text = "0"
    max_rescue = ET.SubElement(root, "MaxRescue")
    max_rescue.text = "10"
    max_items = ET.SubElement(root, "MaxItems")
    max_items.text = "48"
    max_party = ET.SubElement(root, "MaxParty")
    max_party.text = "4"
    turn_limit = ET.SubElement(root, "TurnLimit")
    turn_limit.text = "1000"

    return ET.ElementTree(root)


def create_xml(id: int):
    here = os.path.join("data", "gamedata", "dungeons")
    tree = buildtree()
    ET.indent(tree)
    tree.write(os.path.join(here, str(id), f"dungeon_data{id}.xml"))

for i in range(66, 100):
    create_xml(i)