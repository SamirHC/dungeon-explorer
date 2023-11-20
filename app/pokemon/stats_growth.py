import dataclasses


@dataclasses.dataclass(frozen=True)
class StatsGrowth:
    required_xp: tuple[int]
    hp: tuple[int]
    attack: tuple[int]
    defense: tuple[int]
    sp_attack: tuple[int]
    sp_defense: tuple[int]

    def get_required_xp(self, level: int):
        return self.required_xp[level]

    def get_hp(self, level: int):
        return sum(self.hp[:level+1])

    def get_attack(self, level: int):
        return sum(self.attack[:level+1])

    def get_defense(self, level: int):
        return sum(self.defense[:level+1])

    def get_sp_attack(self, level: int):
        return sum(self.sp_attack[:level+1])

    def get_sp_defense(self, level: int):
        return sum(self.sp_defense[:level+1])