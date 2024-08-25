import os
import xml.etree.ElementTree as ET


def get_tree(id: int):
    file = os.path.join("data", "gamedata", "dungeons", str(id), f"floor_list{id}.xml")
    return ET.parse(file)


def get_floor_list(id: int):
    return get_tree(id).getroot().findall("Floor")


def get_unused(floor: ET.Element):
    return floor.find("FloorLayout").find("Chances").get("unused")


for i in range(100):
    tree = get_tree(i)
    root = tree.getroot()

    for floor_el in root.findall("Floor"):
        # Find the element you want to modify
        element_to_edit = floor_el.find("FloorLayout").find("TerrainSettings")

        # Remove the attribute
        for attr in ("unk1", "unk3", "unk4", "unk5", "unk6", "unk7"):
            if attr in element_to_edit.attrib:
                del element_to_edit.attrib[attr]

        element_to_edit = floor_el.find("FloorLayout").find("Chances")
        if "unused" in element_to_edit.attrib:
            del element_to_edit.attrib["unused"]

    # Save the modified XML to a new file
    tree.write(os.path.join("data", "gamedata", "dungeons", f"floor_list{i}.xml"))
