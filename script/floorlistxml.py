import os
import xml.etree.ElementTree as ET


dirname = os.path.dirname(__file__)
base_dir = os.path.join(dirname, "..", "data", "gamedata", "dungeons")


for file in (f for f in os.listdir(base_dir) if f.endswith(".xml")):
    path = os.path.join(base_dir, file)
    tree = ET.parse(path)
    root = tree.getroot()
    
    
    floor_nodes = root.findall("Floor")
    for fn in floor_nodes:
        monster_list_node = fn.find("MonsterList")
        monster_nodes = monster_list_node.findall("Monster")
        for mn in monster_nodes:
            if mn.attrib["weight"] == "0" == mn.attrib["weight2"]:
                monster_list_node.remove(mn)
        
        trap_list_node = fn.find("TrapList")
        trap_nodes = trap_list_node.findall("Trap")
        for tn in trap_nodes:
            if tn.attrib["weight"] == "0":
                trap_list_node.remove(tn)
    

    # Save the modified XML to a new file
    ET.indent(tree, "  ", level=0)
    #ET.dump(tree)
    tree.write(path)
