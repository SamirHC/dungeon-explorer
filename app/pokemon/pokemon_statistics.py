from app.model.bounded_int import BoundedInt


class PokemonStatistics:
    def __init__(self):
        self.level = BoundedInt(1, 1, 100)
        self.xp = BoundedInt(0, 0, 10_000_000)
        self.hp = BoundedInt(1, 1, 999)
        self.attack = BoundedInt(0, 0, 255)
        self.defense = BoundedInt(0, 0, 255)
        self.sp_attack = BoundedInt(0, 0, 255)
        self.sp_defense = BoundedInt(0, 0, 255)
