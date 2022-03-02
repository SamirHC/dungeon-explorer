from dungeon_explorer.pokemon import pokemon


class Party:
    MAX_MEMBERS = 4

    def __init__(self):
        self.party: list[pokemon.Pokemon] = []

    def __len__(self) -> int:
        return len(self.party)

    def __getitem__(self, index) -> pokemon.Pokemon:
        return self.party[index]

    def __iter__(self):
        return iter(self.party)

    @property
    def user(self) -> pokemon.Pokemon:
        return self.party[0]

    def add(self, user_id: str):
        if len(self) < Party.MAX_MEMBERS:
            self.party.append(pokemon.UserPokemon(user_id))

    def remove(self, p: pokemon.Pokemon):
        self.party.remove(p)

    def is_defeated(self) -> bool:
        return not self.party
