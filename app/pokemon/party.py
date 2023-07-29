from app.common import text
from app.pokemon.pokemon import Pokemon


class Party:
    MAX_MEMBERS = 4

    def __init__(self, members: list[Pokemon]):
        self.members: list[Pokemon] = []
        for member in members:
            self.join(member)
        self.leader = members[0]
        self.leader.name_color = text.BLUE
        
    def __len__(self) -> int:
        return len(self.members)

    def __getitem__(self, index) -> Pokemon:
        return self.members[index]

    def __iter__(self):
        return iter(self.members)

    def join(self, member: Pokemon):
        member.name_color = text.YELLOW
        self.members.append(member)

    def make_leader(self, member_index: int):
        self.leader.name_color = text.YELLOW
        self.members.insert(0, self.members.pop(member_index))
        self.leader = self.members[0]
        self.leader.name_color = text.BLUE

    def standby(self, p: Pokemon):
        self.members.remove(p)
