import os
import xml.etree.ElementTree as ET

from app.common.constants import USERDATA_DIRECTORY
from app.pokemon.pokemon_builder import PokemonBuilder
from app.pokemon.pokemon import Pokemon
from app.pokemon.gender import Gender


def user_pokemon_factory(user_id: int) -> Pokemon:
    file = os.path.join(USERDATA_DIRECTORY, "userteam.xml")
    team_data = ET.parse(file).getroot()

    root = [el for el in team_data.findall("Pokemon") if int(el.get("id")) == user_id][
        0
    ]
    poke_id = int(root.find("PokeID").text)
    return (
        PokemonBuilder(poke_id)
        .set_gender(Gender(int(root.find("Gender").text)))
        .set_level(int(root.find("Level").text))
        .set_xp(int(root.find("XP").text))
        .set_hp(int(root.find("HP").text))
        .set_attack(int(root.find("Attack").text))
        .set_defense(int(root.find("Defense").text))
        .set_sp_attack(int(root.find("SpAttack").text))
        .set_sp_defense(int(root.find("SpDefense").text))
        .set_moves([int(m.get("id")) for m in root.find("Moveset").findall("Move")])
        .build()
    )


def enemy_pokemon_factory(poke_id: int, level: int) -> Pokemon:
    return (
        PokemonBuilder(poke_id)
        .set_level_data(level)
        .set_is_enemy()
        .set_random_gender()
        .build()
    )
