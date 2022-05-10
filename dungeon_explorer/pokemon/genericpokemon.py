import dataclasses
import xml.etree.ElementTree as ET
import os

from dungeon_explorer.dungeon import damage_chart
from dungeon_explorer.pokemon import pokemondata


@dataclasses.dataclass(frozen=True)
class GenericPokemon:
    poke_id: int
    strings: pokemondata.PokemonStrings
    pokedex_number: int
    body_size: int
    type: pokemondata.PokemonType
    movement_type: pokemondata.MovementType
    iq_group: int
    exp_yield: int
    weight: int
    stats_growth: pokemondata.StatsGrowth
    level_up_moves: pokemondata.LevelUpMoves
    egg_moves: tuple[int]
    hm_tm_moves: tuple[int]

    @property
    def name(self) -> str:
        return self.strings.name

    @property
    def category(self) -> str:
        return self.strings.category

    def get_required_xp(self, level: int):
        return self.stats_growth.get_required_xp(level)

    def get_hp(self, level: int):
        return self.stats_growth.get_hp(level)

    def get_attack(self, level: int):
        return self.stats_growth.get_attack(level)

    def get_defense(self, level: int):
        return self.stats_growth.get_defense(level)

    def get_sp_attack(self, level: int):
        return self.stats_growth.get_sp_attack(level)

    def get_sp_defense(self, level: int):
        return self.stats_growth.get_sp_defense(level)

    def get_level_up_move_ids(self, level: int) -> list[int]:
        return self.level_up_moves.get_level_up_move_ids(level)


class GenericPokemonDatabase:
    def __init__(self):
        self.base_dir = os.path.join("data", "gamedata", "pokemon")
        self.loaded: dict[int, GenericPokemon] = {}

    def __getitem__(self, poke_id: int) -> GenericPokemon:
        if poke_id in self.loaded:
            return self.loaded[poke_id]
        self.load(poke_id)
        return self.loaded[poke_id]

    def load(self, poke_id):
        if poke_id in self.loaded:
            return

        file = os.path.join(self.base_dir, f"{poke_id}.xml")
        root = ET.parse(file).getroot()

        strings_element = root.find("Strings").find("English")
        name = strings_element.find("Name").text
        category = strings_element.find("Category").text
        strings = pokemondata.PokemonStrings(name, category)

        gendered_element = root.find("GenderedEntity")
        pokedex_number = int(gendered_element.find("PokedexNumber").text)
        body_size = int(gendered_element.find("BodySize").text)
        type = pokemondata.PokemonType(
            damage_chart.Type(int(gendered_element.find("PrimaryType").text)),
            damage_chart.Type(int(gendered_element.find("SecondaryType").text))
        )
        movement_type = pokemondata.MovementType(int(gendered_element.find("MovementType").text))
        iq_group = int(gendered_element.find("IQGroup").text)
        exp_yield = int(gendered_element.find("ExpYield").text)
        weight = int(gendered_element.find("Weight").text)

        base_stats = gendered_element.find("BaseStats")
        base_hp = int(base_stats.find("HP").text)
        base_attack = int(base_stats.find("Attack").text)
        base_defense = int(base_stats.find("Defense").text)
        base_sp_attack = int(base_stats.find("SpAttack").text)
        base_sp_defense = int(base_stats.find("SpDefense").text)

        stats_growth_element = root.find("StatsGrowth").findall("Level")
        required_xp = [-1]
        hp_growth = [base_hp]
        attack_growth = [base_attack]
        defense_growth = [base_defense]
        sp_attack_growth = [base_sp_attack]
        sp_defense_growth = [base_sp_defense]
        for level in stats_growth_element:
            required_xp.append(int(level.find("RequiredExp").text))
            hp_growth.append(int(level.find("HP").text))
            attack_growth.append(int(level.find("Attack").text))
            defense_growth.append(int(level.find("Defense").text))
            sp_attack_growth.append(int(level.find("SpAttack").text))
            sp_defense_growth.append(int(level.find("SpDefense").text))
        stats_growth = pokemondata.StatsGrowth(
            tuple(required_xp),
            tuple(hp_growth),
            tuple(attack_growth),
            tuple(defense_growth),
            tuple(sp_attack_growth),
            tuple(sp_defense_growth)
        )

        moveset_element = root.find("Moveset")
        levels_learned = []
        moves_learned = []
        for el in moveset_element.find("LevelUpMoves").findall("Learn"):
            levels_learned.append(int(el.find("Level").text))
            moves_learned.append(el.find("MoveID").text)
        level_up_moves = pokemondata.LevelUpMoves(
            tuple(levels_learned),
            tuple(moves_learned)
        )
        egg_moves = [el.text for el in moveset_element.find("EggMoves").findall("MoveID")]
        hm_tm_moves = [el.text for el in moveset_element.find("HmTmMoves").findall("MoveID")]

        res = GenericPokemon(
            poke_id,
            strings,
            pokedex_number,
            body_size,
            type,
            movement_type,
            iq_group,
            exp_yield,
            weight,
            stats_growth,
            level_up_moves,
            egg_moves,
            hm_tm_moves,
        )
        self.loaded[poke_id] = res


db = GenericPokemonDatabase()


def get_poke_id_by_pokedex(dex: int) -> str:
    for i in range(dex, 600):
        poke_id = str(i)
        if db[poke_id].pokedex_number == dex:
            return poke_id