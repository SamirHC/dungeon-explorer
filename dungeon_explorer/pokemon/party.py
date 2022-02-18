from . import pokemon


class Party:
    MAX_MEMBERS = 4

    def __init__(self):
        self.party = []
        self.id_list = []

    def __len__(self) -> int:
        return len(self.party)

    def __getitem__(self, index) -> pokemon.UserPokemon:
        return self.party[index]

    def __iter__(self):
        return iter(self.party)

    @property
    def user(self) -> pokemon.UserPokemon:
        return self.party[0]

    def add(self, user_id: str):
        if len(self) < Party.MAX_MEMBERS:
            self.party.append(pokemon.UserPokemon(user_id))
            self.id_list.append(user_id)

    def remove(self, user_id: str):
        self.party.pop(self.id_list.index(user_id))

    def is_defeated(self) -> bool:
        return not self.party