import os
import xml.etree.ElementTree as ET


def buildtree():
    root = ET.Element("TilesetData")
    secondary_type = ET.SubElement(root, "SecondaryType")
    secondary_type.text = "Water"
    minimap_color = ET.SubElement(root, "MinimapColor")
    minimap_color.text = "000000"
    stirring_effect = ET.SubElement(root, "StirringEffect")
    stirring_effect.text = "Leaves"
    secret_power = ET.SubElement(root, "SecretPower")
    secret_power.text = "Paralysis"
    camouflage = ET.SubElement(root, "Camouflage")
    camouflage.text = "Normal"
    nature_power = ET.SubElement(root, "NaturePower")
    nature_power.text = "Tri Attack"
    weather = ET.SubElement(root, "Weather")
    weather.text = "Foggy 4"
    underwater = ET.SubElement(root, "Underwater")
    underwater.text = "0"

    return ET.ElementTree(root)

def create_xml(id: int):
    here = os.path.join("assets", "images", "tilesets")
    tree = buildtree()
    ET.indent(tree)
    tree.write(os.path.join(here, str(id), f"tileset_data.xml"))

def update_xml(id: int):
    file = os.path.join("assets", "images", "tilesets", str(id), "tileset_data.xml")
    root = ET.parse(file).getroot()
    tree = set_blue_minimap_color(root)
    ET.indent(tree)
    tree.write(file)

def set_blue_minimap_color(root: ET.Element):
    root.find("MinimapColor").text = "0000f8"
    return ET.ElementTree(root)

def set_white_minimap_color(root: ET.Element):
    root.find("MinimapColor").text = "ffffff"
    return ET.ElementTree(root)
