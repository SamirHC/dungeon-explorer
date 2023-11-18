from app.common.constants import USERDATA_DIRECTORY
from app.pokemon.pokemon_builder import PokemonBuilder
from app.pokemon.pokemon import Pokemon


import os
import xml.etree.ElementTree as ET


class UserPokemon(Pokemon):
    def __init__(self, user_id: int):
        self.user_id = user_id
        root = self.get_root()
        poke_id = int(root.find("PokeID").text)
        model = (
            PokemonBuilder(poke_id)
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
        super().__init__(model)

    def get_root(self) -> ET.Element:
        file = os.path.join(USERDATA_DIRECTORY, "userteam.xml")
        team_data = ET.parse(file).getroot()
        for el in team_data.findall("Pokemon"):
            if int(el.get("id")) == self.user_id:
                return el