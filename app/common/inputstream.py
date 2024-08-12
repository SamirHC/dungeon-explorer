import pygame.key


class InputStream:
    """
    A class that manages input streams, including keyboard events.

    The `InputStream` class is responsible for updating and maintaining the
    state of input devices such as the keyboard.
    """
    def __init__(self):
        self.keyboard = Keyboard()

    def update(self):
        """
        Update the input states for all devices.

        This method updates the keyboard's state to reflect the latest key
        press information.
        """
        self.keyboard.update()


class Keyboard:
    """
    A class that handles keyboard input using the Pygame library.

    The `Keyboard` class manages the state of keys, tracking which keys are
    pressed, released, held, or down during each update cycle.
    """
    
    def __init__(self):
        self.previously_pressed = pygame.key.get_pressed()
        self.currently_pressed = pygame.key.get_pressed()

    def update(self):
        """
        Update the keyboard state.

        This method updates the previously pressed and currently pressed key
        states to reflect the latest information from the Pygame event loop.
        """
        self.previously_pressed = self.currently_pressed
        self.currently_pressed = pygame.key.get_pressed()

    def is_pressed(self, key: int) -> bool:
        """
        Check if a key has been pressed since the last update.

        A key is considered pressed if it was not pressed in the previous
        state but is pressed in the current state.

        :param int key: The Pygame key code of the key to check.
        :return: True if the key is newly pressed, False otherwise.
        :rtype: bool
        """
        return not self.previously_pressed[key] and self.currently_pressed[key]

    def is_released(self, key: int) -> bool:
        """
        Check if a key has been released since the last update.

        A key is considered released if it was pressed in the previous state
        but is not pressed in the current state.

        :param int key: The Pygame key code of the key to check.
        :return: True if the key is newly released, False otherwise.
        :rtype: bool
        """
        return self.previously_pressed[key] and not self.currently_pressed[key]

    def is_held(self, key: int) -> bool:
        """
        Check if a key is currently held down.

        A key is considered held if it was pressed in the previous state and
        remains pressed in the current state.

        :param int key: The Pygame key code of the key to check.
        :return: True if the key is held down, False otherwise.
        :rtype: bool
        """
        return self.previously_pressed[key] and self.currently_pressed[key]

    def is_down(self, key: int) -> bool:
        """
        Check if a key is either newly pressed or held down.

        This method combines the logic of `is_pressed` and `is_held` to
        determine if a key is currently active in any form.

        :param int key: The Pygame key code of the key to check.
        :return: True if the key is active, False otherwise.
        :rtype: bool
        """
        return self.is_held(key) or self.is_pressed(key)
