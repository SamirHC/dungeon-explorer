import pygame

from app.common import constants, frame, text, menu, inputstream
from app.pokemon import genericpokemon, portrait
from app.db import genericpokemon_db


class PartnerMenu:
    def __init__(self, leader: genericpokemon.GenericPokemon):
        self.frame = frame.Frame((13, 15)).with_footer_divider()
        partners = self.get_partners(leader)
        portraits = self.get_portraits(partners)
        pages = [[]]
        self.partners = [[]]
        self.portraits = [[]]
        for partner, portrait in zip(partners, portraits):
            name = partner.name
            if len(pages[-1]) == 6:
                pages.append([name])
                self.partners.append([partner])
                self.portraits.append([portrait])
            else:
                pages[-1].append(name)
                self.partners[-1].append(partner)
                self.portraits[-1].append(portrait)
        self.menu = menu.PagedMenuModel(pages)

    def get_partners(self, leader: genericpokemon.GenericPokemon) -> list[genericpokemon.GenericPokemon]:
        res = []
        for poke_id in [1, 4, 7, 25, 152, 155, 158, 280, 283, 286, 422, 425, 428, 133, 438, 489, 258, 37, 328, 52, 488]:
            partner = genericpokemon_db[poke_id]
            if partner.type.type1 is not leader.type.type1:
                res.append(partner)
        return res

    def get_portraits(self, partners: list[genericpokemon.GenericPokemon]) -> list[portrait.PortraitSheet]:
        res = []
        for p in partners:
            dex = p.pokedex_number
            res.append(portrait.db[dex])
        return res

    def get_selection(self) -> genericpokemon.GenericPokemon:
        return self.partners[self.menu.page][self.menu.pointer]

    def get_selected_portrait(self) -> portrait.PortraitSheet:
        return self.portraits[self.menu.page][self.menu.pointer]
    
    def process_input(self, input_stream: inputstream.InputStream):
        kb = input_stream.keyboard
        if kb.is_pressed(constants.OPTION_SCROLL_DOWN_KEY):
            menu.pointer_animation.restart()
            self.menu.next()
        elif kb.is_pressed(constants.OPTION_SCROLL_UP_KEY):
            menu.pointer_animation.restart()
            self.menu.prev()
        elif kb.is_pressed(constants.PAGE_NEXT_KEY):
            menu.pointer_animation.restart()
            self.menu.next_page()
        elif kb.is_pressed(constants.PAGE_PREV_KEY):
            menu.pointer_animation.restart()
            self.menu.prev_page()

    def update(self):
        menu.pointer_animation.update()

    def render(self) -> pygame.Surface:
        self.surface = self.frame.copy()
        x, y = 36, 10
        for name in self.menu.pages[self.menu.page]:
            name_surface = (
                text.TextBuilder()
                .set_shadow(True)
                .set_color(text.LIME)
                .write(name)
                .build()
                .render()
            )
            self.surface.blit(name_surface, (x, y))
            y += 14
        pointer_position = pygame.Vector2(0, 14)*self.menu.pointer + self.frame.container_rect.topleft
        self.surface.blit(menu.pointer_animation.render(), pointer_position)
        return self.surface