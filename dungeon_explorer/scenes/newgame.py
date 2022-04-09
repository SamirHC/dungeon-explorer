import pygame

from dungeon_explorer.common import inputstream, constants, text
from dungeon_explorer.pokemon import party
from dungeon_explorer.scenes import scene, dungeon


class NewGameScene(scene.Scene):
    def __init__(self):
        super().__init__()

    def process_input(self, input_stream: inputstream.InputStream):
        if input_stream.keyboard.is_pressed(pygame.K_RETURN):
            entry_party = party.Party("0")
            entry_party.add("3")
            self.next_scene = dungeon.StartDungeonScene("14", entry_party)

    def update(self):
        pass

    def render(self) -> pygame.Surface:
        surface = pygame.Surface(constants.DISPLAY_SIZE, pygame.SRCALPHA)
        surface.fill(constants.BLACK)
        welcome_text = text.build("Welcome to Pokemon Mystery Dungeon Remake")
        rect = welcome_text.get_rect(center=surface.get_rect().center)
        surface.blit(welcome_text, rect.topleft)
        return surface