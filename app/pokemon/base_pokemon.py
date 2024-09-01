import dataclasses

from app.model.type import PokemonType
from app.pokemon.level_up_moves import LevelUpMoves
from app.pokemon.stats_growth import StatsGrowth
from app.pokemon.movement_type import MovementType
from app.pokemon.gender import Gender


@dataclasses.dataclass(frozen=True)
class GenderedEntity:
    # movement_speed: int
    gender: Gender
    sprite_id: int
    body_size: int
    exp_yield: int
    # recruit_rate: tuple[int]
    weight: int
    # size: int
    # shadow_size: ShadowSize
    # asleep_chance: int
    # hp_regen: int
    # spawn_threshold: int
    # chest_drop_rates
    # personality: Personality
    # evolution_req: EvolutionReq
    # exclusive_items: tuple[int]
    # can_move: bool
    # can_throw_items: bool
    # can_evolve: bool
    # item_required_for_spawning: bool


@dataclasses.dataclass(frozen=True)
class BasePokemon:
    name: str
    category: str
    poke_id: int
    pokedex_number: int
    type: PokemonType
    movement_type: MovementType
    iq_group: int  # IQGroup
    # abilities: tuple[int]
    gendered_entities: dict[Gender, GenderedEntity]
    stats_growth: StatsGrowth
    level_up_moves: LevelUpMoves
    egg_moves: tuple[int]
    hm_tm_moves: tuple[int]


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

    def get_possible_genders(self) -> list[Gender]:
        return list(self.gendered_entities.keys())