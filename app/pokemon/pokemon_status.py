from app.model.bounded_int import BoundedInt
from app.pokemon.stat import Stat
from app.pokemon.status_effect import StatusEffect


class PokemonStatus:
    def __init__(self, hp: int):
        # Special
        self.hp = BoundedInt(hp, 0, hp)
        self.belly = BoundedInt(100, 0, 100)
        self.speed = BoundedInt(1, 0, 4)
        # Stat related
        self.stat_stages = {stat: BoundedInt(0, -10, 10) for stat in Stat}
        self.stat_divider = {stat: BoundedInt(0, 0, 7) for stat in Stat}
        # Conditions
        self.status_conditions: dict[StatusEffect, int] = {}

    def get_expired(self, turn: int) -> set[StatusEffect]:
        return set(
            eff for eff, expiry in self.status_conditions.items() if turn == expiry
        )

    def remove_statuses(self, effects: set[StatusEffect]):
        for eff in effects:
            self.clear_affliction(eff)

    def can_regenerate(self) -> bool:
        return self.status_conditions.keys().isdisjoint(
            (
                StatusEffect.POISONED,
                StatusEffect.BADLY_POISONED,
                StatusEffect.HEAL_BLOCK,
            )
        )

    def restore_stats(self):
        for stat in Stat:
            self.stat_stages[stat].set(0)
            self.stat_divider[stat].set(0)

    def restore_status(self):
        self.status_conditions.clear()

    def has_status_effect(self, status_effect: StatusEffect):
        return status_effect in self.status_conditions

    def afflict(self, status_effect: StatusEffect, expiry: int = -1):
        self.status_conditions[status_effect] = expiry

    def clear_affliction(self, status_effect: StatusEffect):
        if status_effect in self.status_conditions:
            del self.status_conditions[status_effect]

    def is_fainted(self) -> bool:
        return self.hp.value == 0

    def is_asleep(self) -> bool:
        return not self.status_conditions.keys().isdisjoint(
            (StatusEffect.ASLEEP, StatusEffect.NIGHTMARE, StatusEffect.NAPPING)
        )
