import pygame.key

class Keyboard:
    def __init__(self):
        self.previously_pressed = pygame.key.get_pressed()
        self.currently_pressed = pygame.key.get_pressed()

    def update(self):
        self.previously_pressed = self.currently_pressed
        self.currently_pressed = pygame.key.get_pressed()

    def is_pressed(self, key) -> bool:
        return not self.previously_pressed[key] and self.currently_pressed[key]

    def is_released(self, key) -> bool:
        return self.previously_pressed[key] and not self.currently_pressed[key]

    def is_held(self, key) -> bool:
        return self.previously_pressed[key] and self.currently_pressed[key]