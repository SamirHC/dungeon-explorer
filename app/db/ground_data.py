import os
import xml.etree.ElementTree as ET

import pygame

import app.db.map_background as map_background_db
from app.common.constants import GAMEDATA_DIRECTORY
from app.ground.ground_data import EventTrigger, GroundData, GroundSceneData

"""
The story is a sequence of scenes. Each scene is made up of a collection of
ground locations, each making use of different events and npcs.

We need to know what the current scene is, as well as the location in order to
fetch the information from storage.
"""


def parse_node_to_event_trigger(node: ET.Element) -> EventTrigger:
    id = int(node.get("id"))
    event_class = node.get("class")
    data = {k: node.get(k) for k in node.keys()}
    rect = pygame.Rect(
        int(node.get("x")),
        int(node.get("y")),
        int(node.get("w")),
        int(node.get("h")),
    )
    return EventTrigger(id, event_class, rect, data)


def get_ground_scene_data(scene_id: int, location: int = 0) -> GroundSceneData:
    scene_id = scene_id
    location = location
    directory = os.path.join(GAMEDATA_DIRECTORY, "ground", str(scene_id))

    file = os.path.join(directory, f"ground_data{location}.xml")
    root = ET.parse(file).getroot()

    ground_data = get_ground_location_data(root)
    return GroundSceneData(scene_id, ground_data, location)


def get_ground_location_data(root: ET.Element) -> GroundData:
    bg_id = root.find("Background").get("id")
    trigger_nodes = root.find("EventTriggers").findall("Trigger")
    triggers = list(map(parse_node_to_event_trigger, trigger_nodes))

    return GroundData(
        ground_map=map_background_db.load(bg_id),
        event_triggers=triggers,
        npcs=[],  # [pokemon.Pokemon(pokemon.PokemonBuilder(325).build_level(1))]
    )
