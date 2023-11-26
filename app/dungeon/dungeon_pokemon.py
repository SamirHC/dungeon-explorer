from app.pokemon.pokemon import Pokemon
from app.pokemon.pokemon_status import PokemonStatus
from app.model.moving_entity import MovingEntity

class DungeonPokemon:
    """
    A wrapper for the Pokemon class that implements Dungeon specific
    functionality.
    """

    def __init__(self, pokemon: Pokemon, is_enemy: bool = False):
        self.pokemon = pokemon
        self.is_enemy = is_enemy

        self.moving_entity = MovingEntity()
        self.status = PokemonStatus()

        self.has_turn = True
        self.is_fainted = False
