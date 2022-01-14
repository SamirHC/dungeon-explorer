import constants
import pokemon


class MovementSystem:
    def __init__(self):
        self.is_active = False
        self.motion_time_left = 0
        self.time_for_one_tile = constants.WALK_ANIMATION_TIME

        self.moving: list[pokemon.Pokemon] = []

    def add(self, p: pokemon.Pokemon):
        self.moving.append(p)

    def clear(self):
        self.moving.clear()

    def update(self):
        pass