import csv
import os
import xml.etree.ElementTree as ET

def get_type(t: str):
    types = ["Typeless", "Normal", "Fire", "Water", "Grass"
    , "Electric", "Ice", "Fighting", "Poison", "Ground" 
    , "Flying", "Psychic", "Bug", "Rock" 
    , "Ghost", "Dragon", "Dark", "Steel", "Fairy", "Random", "User's 1st type"]
    return str(types.index(t))

def get_category(c: str):
    categories = ["Physical", "Special", "Other"]
    return str(categories.index(c))

def get_range(data: dict[str, str]):
    corner = int(convert(data["Corner"]))
    range = data["Range"]
    target = data["Target"]
    if range == "10 tiles away":
        return "Line of sight"
    if range == "2 tiles away":
        return "Enemy up to 2 tiles away"
    if range == "Adjacent PokÃ©mon":
        return "Enemies within 1-tile range"
    if range in ("User", "User / Adjacent PokÃ©mon", "User / Entire floor", "User / Front", "User Nearby PokÃ©mon"):
        return "User"
    if range == "Nearby PokÃ©mon" and target == "Enemy":
        return "Enemies within 1-tile range"
    if range == "Front" and target == "Enemy" and corner:
        return "Enemy in front, cuts corners"
    if range == "Front" and target == "Enemy" and not corner:
        return "Enemy in front"
    if range == "Front" and target == "All" and corner:
        return "Facing Pokemon, cuts corners"
    if range == "Front" and target == "All" and not corner:
        return "Facing Pokemon"
    if range == "Entire room" and target == "Enemy":
        return "All enemies in the room"
    if range == "Entire room" and target == "Party":
        return "All allies in the room"
    if range == "Entire room" and target == "All":
        return "Everyone in the room"
    if range == "Entire room" and target == "All except user":
        return "Everyone in the room, except the user"
    if range in ("Entire floor", "Tile below user"):
        return "Floor"
    if range == "Varies":
        return "Varies"
    if range == "Item":
        return "Item"
    return ""

def get_accuracy(s: str):
    if s == "Sure Hit":
        return "1000"
    return str(int(float(s)))

def get_power(s: str):
    if s == "2-15":
        return "-1"
    return s
    
def convert(s: str):
    return str(int(s == 'âœ”'))

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
    category.text = get_category(data["Category"])
    stats = ET.SubElement(root, "Stats")
    pp = ET.SubElement(stats, "PP")
    pp.text = data["PP"]
    power = ET.SubElement(stats, "Power")
    power.text = get_power(data["Pwr"])
    accuracy = ET.SubElement(stats, "Accuracy")
    accuracy.text = get_accuracy(data["Accuracy"])
    critical = ET.SubElement(stats, "Critical")
    critical.text = data["Crit"]
    animation = ET.SubElement(root, "Animation")
    animation.text = "Attack"
    chained_hits = ET.SubElement(root, "ChainedHits")
    chained_hits.text = "1"
    range = ET.SubElement(root, "Range")
    range.text = get_range(data)
    flags = ET.SubElement(root, "Flags")
    ginseng = ET.SubElement(flags, "Ginseng")
    ginseng.text = convert(data["Ginseng"])
    magic_coat = ET.SubElement(flags, "MagicCoat")
    magic_coat.text = convert(data["Magic Coat"])
    snatch = ET.SubElement(flags, "Snatch")
    snatch.text = convert(data["Snatch"])
    muzzled = ET.SubElement(flags, "Muzzled")
    muzzled.text = convert(data["Muzzled"])
    taunt = ET.SubElement(flags, "Taunt")
    taunt.text = convert(data["Taunt"])
    frozen = ET.SubElement(flags, "Frozen")
    frozen.text = "0"
    effect = ET.SubElement(flags, "Effect")
    effect.text = "0"
    ai = ET.SubElement(root, "AI")
    weight = ET.SubElement(ai, "Weight")
    weight.text = data["Weight"]
    activation_condition = ET.SubElement(ai, "ActivationCondition")
    activation_condition.text = "None"
    return ET.ElementTree(root)

def create_xml():
    here = os.path.join("data", "gamedata", "moves")
    with open(os.path.join(here, "movelist.csv"), newline="") as csvfile:
        rows = csv.DictReader(csvfile)
        for row in rows:
            tree = buildtree(row)
            ET.indent(tree)
            id = tree.getroot().attrib["id"]
            tree.write(os.path.join(here, f"{id}.xml"))

create_xml()