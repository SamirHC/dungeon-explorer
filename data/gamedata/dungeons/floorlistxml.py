import os
import xml.etree.ElementTree as ET


def get_tree(id: int):
    file = os.path.join("data", "gamedata", "dungeons", str(id), f"floor_list{id}.xml")
    return ET.parse(file)

def get_floor_list(id: int):
    return get_tree(id).getroot().findall("Floor")

def get_unused(floor: ET.Element):
    return floor.find("FloorLayout").find("Chances").get("unused")

def get_unk1(floor: ET.Element):
    return int(floor.find("FloorLayout").find("TerrainSettings").get("unk1"))

def get_unk3(floor: ET.Element):
    return int(floor.find("FloorLayout").find("TerrainSettings").get("unk3"))

def get_unk4(floor: ET.Element):
    return int(floor.find("FloorLayout").find("TerrainSettings").get("unk4"))

def get_unk5(floor: ET.Element):
    return int(floor.find("FloorLayout").find("TerrainSettings").get("unk5"))

def get_unk6(floor: ET.Element):
    return int(floor.find("FloorLayout").find("TerrainSettings").get("unk6"))

def get_unk7(floor: ET.Element):
    return int(floor.find("FloorLayout").find("TerrainSettings").get("unk7"))

def get_unkE(floor: ET.Element):
    return int(floor.find("FloorLayout").find("MiscSettings").get("unkE"))

data = {1: [], 3: [], 4:[], 5:[], 6:[], 7:[], "E":[]}
for i in range(100):
    for n, floor in enumerate(get_floor_list(i)):
        location = (i, n)
        if get_unk1(floor):
            data[1].append(location)
        if get_unk3(floor):
            data[3].append(location)
        if get_unk4(floor):
            data[4].append(location)
        if get_unk5(floor):
            data[5].append(location)
        if get_unk6(floor):
            data[6].append(location)
        if get_unk7(floor):
            data[7].append(location)
        if get_unkE(floor):
            data["E"].append(location)

print(data)