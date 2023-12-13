from __future__ import annotations

import app.db.database as db
from app.move.moveset import Moveset
from app.pokemon.pokemon_statistics import PokemonStatistics
from app.pokemon.pokemon import Pokemon

import random


class PokemonBuilder:
    def __init__(self, poke_id: int):
        self.generic_data = db.genericpokemon_db[poke_id]
        self.stats = PokemonStatistics()
        self.moveset = Moveset()
        self.is_enemy = False

    def set_is_enemy(self):
        self.is_enemy = True
        return self

    def set_level(self, val: int):
        self.stats.level.set(val)
        return self

    def set_xp_from_level(self):
        level_val = self.stats.level.value
        xp_val = self.generic_data.get_required_xp(level_val)
        self.stats.xp.set(xp_val)
        return self

    def set_xp(self, val: int):
        self.stats.xp.set(val)
        return self

    def set_hp(self, val: int):
        self.stats.hp.set(val)
        return self

    def set_attack(self, val: int):
        self.stats.attack.set(val)
        return self

    def set_defense(self, val: int):
        self.stats.defense.set(val)
        return self

    def set_sp_attack(self, val: int):
        self.stats.sp_attack.set(val)
        return self

    def set_sp_defense(self, val: int):
        self.stats.sp_defense.set(val)
        return self

    def set_stats_from_level(self):
        self.set_xp_from_level()
        level_val = self.stats.level.value
        self.set_hp(self.generic_data.get_hp(level_val))
        self.set_attack(self.generic_data.get_attack(level_val))
        self.set_defense(self.generic_data.get_defense(level_val))
        self.set_sp_attack(self.generic_data.get_sp_attack(level_val))
        self.set_sp_defense(self.generic_data.get_sp_defense(level_val))
        return self

    def set_moves(self, move_ids: list[int]):
        for move_id in move_ids:
            self.moveset.learn(move_id)
        return self

    def set_moves_from_level(self):
        level_val = self.stats.level.value
        possible_move_ids = self.generic_data.get_level_up_move_ids(level_val)
        if len(possible_move_ids) > 4:
            selected_move_ids = random.sample(possible_move_ids, 4)
        else:
            selected_move_ids = possible_move_ids
        return self.set_moves(selected_move_ids)

    def build(self) -> Pokemon:
        return Pokemon(self.generic_data, self.stats, self.moveset, self.is_enemy)

    def set_level_data(self, level: int) -> PokemonBuilder:
        return self.set_level(level).set_stats_from_level().set_moves_from_level()
