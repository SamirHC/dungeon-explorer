import pygame.key
import pygame.mouse


class InputStream:
    def __init__(self):
        self.keyboard = Keyboard()
        self.mouse = Mouse()

    def update(self):
        self.keyboard.update()
        self.mouse.update()


class Mouse:
    def __init__(self):
        self.previously_pressed = pygame.mouse.get_pressed()
        self.currently_pressed = pygame.mouse.get_pressed()
        self.previous_position = pygame.mouse.get_pos()
        self.current_position = pygame.mouse.get_pos()

    def update(self):
        self.previously_pressed = self.currently_pressed
        self.currently_pressed = pygame.key.get_pressed()
        self.previous_position = self.current_position
        self.current_position = pygame.mouse.get_pos()

    def is_pressed(self, key: int) -> bool:
        return not self.previously_pressed[key] and self.currently_pressed[key]

    def is_released(self, key: int) -> bool:
        return self.previously_pressed[key] and not self.currently_pressed[key]

    def is_held(self, key: int) -> bool:
        return self.previously_pressed[key] and self.currently_pressed[key]


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
