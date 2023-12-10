from app.model.statistic import Statistic


class PokemonStatistics:
    def __init__(self):
        self.level = Statistic(1, 1, 100)
        self.xp = Statistic(0, 0, 10_000_000)
        self.hp = Statistic(1, 1, 999)
        self.attack = Statistic(0, 0, 255)
        self.defense = Statistic(0, 0, 255)
        self.sp_attack = Statistic(0, 0, 255)
        self.sp_defense = Statistic(0, 0, 255)
