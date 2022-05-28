import csv
import os
import xml.etree.ElementTree as ET

with open(os.path.join("data", "gamedata", "moves", "movedata.csv"), newline="") as file:
    movedata_csv = csv.DictReader(file)
    movedata_dict = {row["[Name]"]: row for row in movedata_csv}

def get_type(t: str):
    types = ["Typeless", "Normal", "Fire", "Water", "Grass"
    , "Electric", "Ice", "Fighting", "Poison", "Ground" 
    , "Flying", "Psychic", "Bug", "Rock" 
    , "Ghost", "Dragon", "Dark", "Steel", "Fairy", "Random", "User's 1st type"]
    return str(types.index(t))

def get_accuracy(s: str):
    return str(int(float(s)))

def get_power(s: str):
    if s == "2-15":
        return "-1"
    return s

def get_effect(name: str):
    return movedata_dict[name]["[Other Flags]"][1:]

def buildtree(data: dict[str, str]):
    root = ET.Element("Move")
    root.attrib["id"] = data["ID"]
    name = ET.SubElement(root, "Name")
    name.text = data["Name"]
    description = ET.SubElement(root, "Description")
    description.text = data["Description"]
    type = ET.SubElement(root, "Type")
    type.text = get_type(data["Type"])
    category = ET.SubElement(root, "Category")
    category.text = data["Category"]
    stats = ET.SubElement(root, "Stats")
    pp = ET.SubElement(stats, "PP")
    pp.text = data["PP"]
    power = ET.SubElement(stats, "Power")
    power.text = get_power(data["Power"])
    accuracy = ET.SubElement(stats, "Accuracy")
    accuracy.text = get_accuracy(data["Accuracy"])
    critical = ET.SubElement(stats, "Critical")
    critical.text = data["Critical"]
    animation = ET.SubElement(root, "Animation")
    animation.text = data["Animation"]
    chained_hits = ET.SubElement(root, "ChainedHits")
    chained_hits.text = "1"
    range = ET.SubElement(root, "Range")
    range.text = data["Range"]
    flags = ET.SubElement(root, "Flags")
    ginseng = ET.SubElement(flags, "Ginseng")
    ginseng.text = data["Ginseng"]
    magic_coat = ET.SubElement(flags, "MagicCoat")
    magic_coat.text = data["Magic Coat"]
    snatch = ET.SubElement(flags, "Snatch")
    snatch.text = data["Snatch"]
    muzzled = ET.SubElement(flags, "Muzzled")
    muzzled.text = data["Muzzled"]
    taunt = ET.SubElement(flags, "Taunt")
    taunt.text = data["Taunt"]
    frozen = ET.SubElement(flags, "Frozen")
    frozen.text = "0"
    effect = ET.SubElement(flags, "Effect")
    effect.text = get_effect(name.text)
    ai = ET.SubElement(root, "AI")
    weight = ET.SubElement(ai, "Weight")
    weight.text = data["Weight"]
    activation_condition = ET.SubElement(ai, "ActivationCondition")
    activation_condition.text = "None"
    return ET.ElementTree(root)

def create_xml():
    here = os.path.join("data", "gamedata", "moves")
    with open(os.path.join(here, "movelist_v2.csv"), newline="") as csvfile:
        rows = csv.DictReader(csvfile)
        for row in rows:
            tree = buildtree(row)
            ET.indent(tree)
            id = tree.getroot().attrib["id"]
            tree.write(os.path.join(here, f"{id}.xml"))

create_xml()