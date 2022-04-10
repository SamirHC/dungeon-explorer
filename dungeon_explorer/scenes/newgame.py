import pygame

from dungeon_explorer.common import inputstream, constants, text
from dungeon_explorer.pokemon import party
from dungeon_explorer.scenes import scene, dungeon


class NewGameScene(scene.Scene):
    def __init__(self):
        super().__init__()
        self.scroll_texts = [
            text.ScrollText("Welcome!"),
            text.ScrollText("This is the portal that leads to the\nworld inhabited only by Pokemon."),
            text.ScrollText("Beyond this gateway, many new\nadventures and fresh experiences\nawait your arrival!"),
            text.ScrollText("Before you depart for adventure,\nyou must answer some questions."),
            text.ScrollText("Be truthful when you answer them!"),
            text.ScrollText("Now, are you ready?"),
            text.ScrollText("Then... let the questions begin!")
        ]
        self.index = 0
    
    @property
    def current_text(self) -> text.ScrollText:
        return self.scroll_texts[self.index]

    def process_input(self, input_stream: inputstream.InputStream):
        if input_stream.keyboard.is_pressed(pygame.K_RETURN):
            if self.index != len(self.scroll_texts) - 1:
                self.index += 1
            else:
                entry_party = party.Party("0")
                entry_party.add("3")
                self.next_scene = dungeon.StartDungeonScene("14", entry_party)

    def update(self):
        self.current_text.update()

    def render(self) -> pygame.Surface:
        surface = pygame.Surface(constants.DISPLAY_SIZE, pygame.SRCALPHA)
        surface.fill(constants.BLACK)
        rect = self.current_text.empty_surface.get_rect(center=surface.get_rect().center)
        surface.blit(self.current_text.render(), rect.topleft)
        return surface