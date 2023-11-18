# Stores basic pokemon info
from app.move.moveset import Moveset
from app.pokemon import pokemon_data
from app.pokemon.generic_pokemon import GenericPokemon


import dataclasses


@dataclasses.dataclass
class PokemonModel:
    generic_data: GenericPokemon
    stats: pokemon_data.PokemonStatistics
    moveset: Moveset