from dungeon_explorer.pokemon import pokemon


class Party:
    MAX_MEMBERS = 4

    def __init__(self, members: list[pokemon.Pokemon]):
        self.members: list[pokemon.Pokemon] = []
        for member in members:
            self.join(member)
        
    def __len__(self) -> int:
        return len(self.members)

    def __getitem__(self, index) -> pokemon.Pokemon:
        return self.members[index]

    def __iter__(self):
        return iter(self.members)

    @property
    def leader(self) -> pokemon.Pokemon:
        return self.members[0]

    def join(self, member: pokemon.Pokemon):
        if len(self) < Party.MAX_MEMBERS:
            self.members.append(member)

    def standby(self, p: pokemon.Pokemon):
        self.members.remove(p)
