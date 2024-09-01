import os
import xml.etree.ElementTree as ET

dirname = os.path.dirname(__file__)
base_dir = os.path.join(dirname, "..", "data", "gamedata", "pokemon")

def add_sprite_id(file):
    tree = ET.parse(file)
    root = tree.getroot()
        
    gs = root.findall("GenderedEntity")
    el = ET.Element("SpriteID")
    el.text = "-1"
    
    for g in gs:
        g.append(el)
    
    ET.indent(tree, " ", level=0)
    #ET.dump(root)
    #tree.write(file)

for f in os.listdir(base_dir):
    add_sprite_id(os.path.join(base_dir, f))
