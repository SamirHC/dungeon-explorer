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

    def start(self):
        self.motion_time_left = self.time_for_one_tile

    def update(self):
        if not self.is_active:
            self.is_active = True
            self.start()

        if self.motion_time_left > 0:
            self.motion_time_left -= 1

            for p in self.moving:
                p.motion_animation(self.motion_time_left, self.time_for_one_tile)
        else:
            self.clear()
            self.is_active = False
            