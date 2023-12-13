from app.model.bounded_int import BoundedInt
from app.pokemon.stat import Stat
from app.pokemon.status_effect import StatusEffect


class PokemonStatus:
    def __init__(self):
        # Special
        self.hp = BoundedInt(1, 0, 1)
        self.belly = BoundedInt(100, 0, 100)
        self.speed = BoundedInt(1, 0, 4)
        # Stat related
        self.stat_stages = {stat: BoundedInt(10, 0, 20) for stat in Stat}
        self.stat_divider = {stat: BoundedInt(0, 0, 7) for stat in Stat}
        # Conditions
        self.status_conditions = set()

    def can_regenerate(self) -> bool:
        return self.status_conditions.isdisjoint(
            (
                StatusEffect.POISONED,
                StatusEffect.BADLY_POISONED,
                StatusEffect.HEAL_BLOCK,
            )
        )

    def restore_stats(self):
        for stat in Stat:
            self.stat_stages[stat].set(10)
            self.stat_divider[stat].set(0)

    def restore_status(self):
        self.status_conditions.clear()

    def has_status_effect(self, status_effect: StatusEffect):
        return status_effect in self.status_conditions

    def afflict(self, status_effect: StatusEffect):
        self.status_conditions.add(status_effect)

    def clear_affliction(self, status_effect: StatusEffect):
        self.status_conditions.discard(status_effect)
