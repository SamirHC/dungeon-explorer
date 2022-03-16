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

for i in range(1, 170):
    create_xml(i)