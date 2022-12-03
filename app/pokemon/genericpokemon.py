import dataclasses
from app.pokemon import pokemondata


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
