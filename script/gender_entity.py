import os
import xml.etree.ElementTree as ET

dirname = os.path.dirname(__file__)
base_dir = os.path.join(dirname, "..", "data", "gamedata", "pokemon")

def change_poke_id(file):
    tree = ET.parse(file)
    root = tree.getroot()
        
    #gs = root.findall("GenderedEntity")
    ms = root.findall("Moveset")
    
    
    root.remove(ms[1])
    #"""
    
    #el = None
    
    #for g in gs:
    #    node = g.find("BaseStats")
    #    el = node
    #    g.remove(node)
    
    #root.append(el)

    ET.indent(tree, " ", level=0)
    #ET.dump(root)
    tree.write(file)

for f in os.listdir(base_dir):
    change_poke_id(os.path.join(base_dir, f))
    #break
