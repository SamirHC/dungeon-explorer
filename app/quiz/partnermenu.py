import pygame

from app.common.action import Action
from app.common.inputstream import InputStream
from app.common import settings, menu
from app.gui.frame import Frame
from app.gui import text
from app.pokemon.generic_pokemon import GenericPokemon
from app.pokemon.portrait import PortraitSheet
import app.db.database as db


class PartnerMenu:
    def __init__(self, leader: GenericPokemon):
        self.frame = Frame((13, 15)).with_footer_divider()
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

    def get_partners(self, leader: GenericPokemon) -> list[GenericPokemon]:
        res = []
        for poke_id in [
            1,
            4,
            7,
            25,
            152,
            155,
            158,
            280,
            283,
            286,
            422,
            425,
            428,
            133,
            438,
            489,
            258,
            37,
            328,
            52,
            488,
        ]:
            partner = db.genericpokemon_db[poke_id]
            if partner.type.type1 is not leader.type.type1:
                res.append(partner)
        return res

    def get_portraits(self, partners: list[GenericPokemon]) -> list[PortraitSheet]:
        res = []
        for p in partners:
            dex = p.pokedex_number
            res.append(db.portrait_db[dex])
        return res

    def get_selection(self) -> GenericPokemon:
        return self.partners[self.menu.page][self.menu.pointer]

    def get_selected_portrait(self) -> PortraitSheet:
        return self.portraits[self.menu.page][self.menu.pointer]

    def process_input(self, input_stream: InputStream):
        kb = input_stream.keyboard
        if kb.is_pressed(settings.get_key(Action.DOWN)):
            db.pointer_animation.restart()
            self.menu.next()
        elif kb.is_pressed(settings.get_key(Action.UP)):
            db.pointer_animation.restart()
            self.menu.prev()
        elif kb.is_pressed(settings.get_key(Action.RIGHT)):
            db.pointer_animation.restart()
            self.menu.next_page()
        elif kb.is_pressed(settings.get_key(Action.LEFT)):
            db.pointer_animation.restart()
            self.menu.prev_page()

    def update(self):
        db.pointer_animation.update()

    def render(self) -> pygame.Surface:
        self.surface = self.frame.copy()
        x, y = 36, 10
        for name in self.menu.pages[self.menu.page]:
            name_surface = text.TextBuilder.build_color(text.LIME, name).render()
            self.surface.blit(name_surface, (x, y))
            y += 14
        pointer_position = (
            pygame.Vector2(0, 14) * self.menu.pointer
            + self.frame.container_rect.topleft
        )
        self.surface.blit(db.pointer_animation.get_current_frame(), pointer_position)
        return self.surface
