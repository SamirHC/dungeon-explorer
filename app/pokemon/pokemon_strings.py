import dataclasses


@dataclasses.dataclass(frozen=True)
class PokemonStrings:
    name: str
    category: str
