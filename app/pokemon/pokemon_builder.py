from __future__ import annotations

from app.common.constants import RNG as random
import app.db.base_pokemon as base_pokemon_db
from app.move.moveset import Moveset
from app.pokemon.pokemon_statistics import PokemonStatistics
from app.pokemon.pokemon import Pokemon
from app.pokemon.gender import Gender


class PokemonBuilder:
    def __init__(self, poke_id: int):
        self.base = base_pokemon_db.load(poke_id)
        self.stats = PokemonStatistics()
        self.moveset = Moveset()
        self.is_enemy = False
        self.gender = Gender.INVALID

    def set_gender(self, gender: Gender) -> PokemonBuilder:
        if gender in self.base.get_possible_genders():
            self.gender = gender
        return self

    def set_random_gender(self) -> PokemonBuilder:
        self.gender = random.choice(self.base.get_possible_genders())
        return self

    def set_is_enemy(self) -> PokemonBuilder:
        self.is_enemy = True
        return self

    def set_level(self, val: int) -> PokemonBuilder:
        self.stats.level.set(val)
        return self

    def set_xp_from_level(self) -> PokemonBuilder:
        level_val = self.stats.level.value
        xp_val = self.base.get_required_xp(level_val)
        self.stats.xp.set(xp_val)
        return self

    def set_xp(self, val: int) -> PokemonBuilder:
        self.stats.xp.set(val)
        return self

    def set_hp(self, val: int) -> PokemonBuilder:
        self.stats.hp.set(val)
        return self

    def set_attack(self, val: int) -> PokemonBuilder:
        self.stats.attack.set(val)
        return self

    def set_defense(self, val: int) -> PokemonBuilder:
        self.stats.defense.set(val)
        return self

    def set_sp_attack(self, val: int) -> PokemonBuilder:
        self.stats.sp_attack.set(val)
        return self

    def set_sp_defense(self, val: int) -> PokemonBuilder:
        self.stats.sp_defense.set(val)
        return self

    def set_stats_from_level(self) -> PokemonBuilder:
        self.set_xp_from_level()
        level_val = self.stats.level.value
        self.set_hp(self.base.get_hp(level_val))
        self.set_attack(self.base.get_attack(level_val))
        self.set_defense(self.base.get_defense(level_val))
        self.set_sp_attack(self.base.get_sp_attack(level_val))
        self.set_sp_defense(self.base.get_sp_defense(level_val))
        return self

    def set_moves(self, move_ids: list[int]) -> PokemonBuilder:
        for move_id in move_ids:
            self.moveset.learn(move_id)
        return self

    def set_moves_from_level(self) -> PokemonBuilder:
        level_val = self.stats.level.value
        possible_move_ids = self.base.get_level_up_move_ids(level_val)
        if len(possible_move_ids) > 4:
            selected_move_ids = random.sample(possible_move_ids, 4)
        else:
            selected_move_ids = possible_move_ids
        return self.set_moves(selected_move_ids)

    def build(self) -> Pokemon:
        return Pokemon(self.base, self.stats, self.moveset, self.gender ,self.is_enemy)

    def set_level_data(self, level: int) -> PokemonBuilder:
        return self.set_level(level).set_stats_from_level().set_moves_from_level()

    def build_level(self, level: int) -> Pokemon:
        return self.set_level_data(level).set_random_gender().build()
