from app.pokemon.pokemon_builder import PokemonBuilder
from app.pokemon.pokemon import Pokemon


class EnemyPokemon(Pokemon):
    def __init__(self, poke_id: str, level: int):
        model = (
            PokemonBuilder(poke_id)
            .build_level(level)
        )
        super().__init__(model)
