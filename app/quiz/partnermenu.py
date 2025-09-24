import pygame

from app.common.action import Action
from app.common.inputstream import InputStream
from app.common import settings, menu
from app.gui.frame import Frame
from app.gui import text
from app.pokemon.base_pokemon import BasePokemon
from app.pokemon.portrait import PortraitSheet
from app.pokemon.gender import Gender
import app.db.database as db
import app.db.base_pokemon as base_pokemon_db
import app.db.portrait as portrait_db


class PartnerMenu:
    def __init__(self, leader: BasePokemon):
        self.frame = Frame((13, 15)).with_footer_divider()
        partners = self.get_partners(leader)
        portraits = self.get_portraits(partners)
        pages = [[]]
        self.partners = [[]]
        self.portraits = [[]]
        for partner, portrait in zip(partners, portraits):
            name_surface = (
                text.TextBuilder()
                .set_shadow(True)
                .set_color(constants.OFF_WHITE)
                .write("  ")
                .write(
                    Gender(
                        db.main_db.execute(
                            "SELECT gender FROM partners WHERE poke_id = ?",
                            (partner.poke_id,),
                        ).fetchone()[0]
                    ).get_font_string()
                )
                .write("  ")
                .set_color(constants.LIME)
                .write(partner.name)
                .build()
                .render()
            )
            if len(pages[-1]) == 6:
                pages.append([name_surface])
                self.partners.append([partner])
                self.portraits.append([portrait])
            else:
                pages[-1].append(name_surface)
                self.partners[-1].append(partner)
                self.portraits[-1].append(portrait)
        self.menu = menu.PagedMenuModel(pages)
        self.pointer_animation = db.get_pointer_animation()

    def get_partners(self, leader: BasePokemon) -> list[BasePokemon]:
        res = []
        for (poke_id,) in db.main_db.execute("SELECT poke_id FROM partners").fetchall():
            partner = base_pokemon_db.load(poke_id)
            if partner.type.type1 is not leader.type.type1:
                res.append(partner)
        return res

    def get_portraits(self, partners: list[BasePokemon]) -> list[PortraitSheet]:
        res = []
        for p in partners:
            dex = p.pokedex_number
            res.append(portrait_db.load(dex))
        return res

    def get_selection(self) -> BasePokemon:
        return self.partners[self.menu.page][self.menu.pointer]

    def get_selected_portrait(self) -> PortraitSheet:
        return self.portraits[self.menu.page][self.menu.pointer]

    def process_input(self, input_stream: InputStream):
        kb = input_stream.keyboard
        if kb.is_pressed(settings.get_key(Action.DOWN)):
            self.pointer_animation.restart()
            self.menu.next()
        elif kb.is_pressed(settings.get_key(Action.UP)):
            self.pointer_animation.restart()
            self.menu.prev()
        elif kb.is_pressed(settings.get_key(Action.RIGHT)):
            self.pointer_animation.restart()
            self.menu.next_page()
        elif kb.is_pressed(settings.get_key(Action.LEFT)):
            self.pointer_animation.restart()
            self.menu.prev_page()

    def update(self):
        self.pointer_animation.update()

    def render(self) -> pygame.Surface:
        self.surface = self.frame.copy()
        x, y = 14, 10
        for name_surface in self.menu.pages[self.menu.page]:
            self.surface.blit(name_surface, (x, y))
            y += 14
        pointer_position = (
            pygame.Vector2(0, 14) * self.menu.pointer
            + self.frame.container_rect.topleft
            + (0, 2)
        )
        self.surface.blit(self.pointer_animation.get_current_frame(), pointer_position)
        return self.surface
