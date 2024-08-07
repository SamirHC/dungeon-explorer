import pygame.key


class InputStream:
    def __init__(self):
        self.keyboard = Keyboard()

    def update(self):
        self.keyboard.update()


class Keyboard:
    def __init__(self):
        self.previously_pressed = pygame.key.get_pressed()
        self.currently_pressed = pygame.key.get_pressed()

    def update(self):
        self.previously_pressed = self.currently_pressed
        self.currently_pressed = pygame.key.get_pressed()

    def is_pressed(self, key: int) -> bool:
        return not self.previously_pressed[key] and self.currently_pressed[key]

    def is_released(self, key: int) -> bool:
        return self.previously_pressed[key] and not self.currently_pressed[key]

    def is_held(self, key: int) -> bool:
        return self.previously_pressed[key] and self.currently_pressed[key]

    def is_down(self, key: int) -> bool:
        return self.is_held(key) or self.is_pressed(key)
