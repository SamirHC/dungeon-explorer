import xml.etree.ElementTree as ET
import os

from dungeon_explorer.move import move
from dungeon_explorer.dungeon import damage_chart
from dungeon_explorer.pokemon import pokemondata


class GenericPokemon:
    def __init__(self, poke_id):
        self.poke_id = poke_id

        file = self.get_file()
        tree = ET.parse(file)
        root = tree.getroot()

        self._name = root.find("Strings").find("English").find("Name").text
        self._pokedex_number = int(root.find("GenderedEntity").find("PokedexNumber").text)

        self._type = pokemondata.PokemonType(
            damage_chart.Type(int(root.find("GenderedEntity").find("PrimaryType").text)),
            damage_chart.Type(int(root.find("GenderedEntity").find("SecondaryType").text))
        )
        self._movement_type = pokemondata.MovementType(int(root.find("GenderedEntity").find("MovementType").text))

        base_stats = root.find("GenderedEntity").find("BaseStats")
        self._base_hp = int(base_stats.find("HP").text)
        self._base_attack = int(base_stats.find("Attack").text)
        self._base_defense = int(base_stats.find("Defense").text)
        self._base_sp_attack = int(base_stats.find("SpAttack").text)
        self._base_sp_defense = int(base_stats.find("SpDefense").text)

        stats_growth = root.find("StatsGrowth").findall("Level")
        self._required_xp = []
        self._hp_growth = []
        self._attack_growth = []
        self._defense_growth = []
        self._sp_attack_growth = []
        self._sp_defense_growth = []
        for level in stats_growth:
            self._required_xp.append(int(level.find("RequiredExp").text))
            self._hp_growth.append(int(level.find("HP").text))
            self._attack_growth.append(int(level.find("Attack").text))
            self._defense_growth.append(int(level.find("Defense").text))
            self._sp_attack_growth.append(int(level.find("SpAttack").text))
            self._sp_defense_growth.append(int(level.find("SpDefense").text))

        moveset = root.find("Moveset")
        self._level_up_moves = [(int(el.find("Level").text), el.find("MoveID").text) for el in moveset.find("LevelUpMoves").findall("Learn")]

    def get_file(self):
        return os.path.join("data", "gamedata", "pokemon", f"{self.poke_id}.xml")

    @property
    def name(self) -> str:
        return self._name

    @property
    def pokedex_number(self) -> int:
        return self._pokedex_number

    @property
    def type(self) -> pokemondata.PokemonType:
        return self._type

    @property
    def movement_type(self) -> pokemondata.MovementType:
        return self._movement_type

    def get_required_xp(self, level: int):
        return self._required_xp[level]

    def get_hp(self, level: int):
        return self._base_hp + sum(self._hp_growth[:level])

    def get_attack(self, level: int):
        return self._base_attack + sum(self._attack_growth[:level])

    def get_defense(self, level: int):
        return self._base_defense + sum(self._defense_growth[:level])

    def get_sp_attack(self, level: int):
        return self._base_sp_attack + sum(self._sp_attack_growth[:level])

    def get_sp_defense(self, level: int):
        return self._base_sp_defense + sum(self._sp_defense_growth[:level])

    def get_level_up_moves(self, level: int):
        res = []
        for lv, move_id in self._level_up_moves:
            if lv > level:
                break
            res.append(move.load_move(move_id))
        return res


def get_poke_id_by_pokedex(dex: int) -> str:
    for i in range(dex, 600):
        poke_id = str(i)
        if GenericPokemon(poke_id).pokedex_number == dex:
            return poke_id