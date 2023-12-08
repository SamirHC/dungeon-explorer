import math
import os
import xml.etree.ElementTree as ET

import pygame
import pygame.image
import pygame.transform

from app.common.action import Action
from app.common.inputstream import InputStream
from app.common import constants, text, menu, mixer, settings
from app.model.frame import Frame, PortraitFrame
import app.pokemon.pokemon_builder
from app.pokemon.party import Party
from app.pokemon.portrait import PortraitEmotion
from app.pokemon import pokemon
from app.quiz.partnermenu import PartnerMenu
from app.quiz.quiz import Quiz
from app.quiz.questions import Question
from app.scenes.scene import Scene
from app.scenes.groundscene import StartGroundScene
import app.db.database as db
from app.common.constants import IMAGES_DIRECTORY


class QuizScene(Scene):
    def __init__(self):
        super().__init__(100, 100)
        self.in_quiz = False
        self.in_description = False
        self.in_leader = False
        self.in_partner = False
        self.in_end = False

        self.init_bg()
        self.init_quiz()
        self.init_music()
        self.frame = Frame((30, 7), 255)        

    def init_bg(self):
        self.lower_bg = pygame.image.load(os.path.join(IMAGES_DIRECTORY, "bg", "quiz", "lower.png"))
        self.lower_x = 0
        self.higher_bg = pygame.image.load(os.path.join(IMAGES_DIRECTORY, "bg", "quiz", "higher.png"))
        self.higher_x = 0
        anim_root = ET.parse(os.path.join(IMAGES_DIRECTORY, "bg", "quiz", "palette_data.xml")).getroot()
        self.frames = [[pygame.Color(f"#{color.text}") for color in frame.findall("Color")] for frame in anim_root.findall("Frame")]
        self.bg_t = 0
        self.frame_index = 0

    def init_quiz(self):
        self.quiz = Quiz()
        self.in_quiz = True
        self.current_option_menu = self.build_menu()
        self.current_scroll_text = self.build_question_scroll_text(self.quiz.current_question)

    def init_music(self):
        mixer.set_bgm(-2)

    def init_description(self):
        self.in_description = True
        self.description_scroll_texts = [
            text.ScrollText(
                text.TextBuilder()
                .set_shadow(True)
                .set_color(text.WHITE)
                .write("Thank you for answering all those questions.")
                .build()
            )
        ] + self.build_description_scroll_texts()
        self.description_index = 0
        self.current_scroll_text = self.description_scroll_texts[self.description_index]

    def init_leader(self):
        self.in_leader = True
        self.current_scroll_text = self.build_leader_scroll_text()
        self.portrait_frame = PortraitFrame()
        self.leader_portrait = db.portrait_db[self.quiz.leader.pokedex_number]

    def init_partner(self):
        self.in_partner = True
        self.partner_scroll_texts = self.build_partner_scroll_texts()
        self.partner_index = 0
        self.current_scroll_text = self.partner_scroll_texts[self.partner_index]
        self.partner_menu = PartnerMenu(self.quiz.leader)
        self.NORMAL_PORTRAIT_TIME = 30
        self.partner_portrait_normal_time = self.NORMAL_PORTRAIT_TIME
        self.partner_emotion = PortraitEmotion.NORMAL

    def init_end(self):
        self.in_end = True
        self.end_scroll_texts = self.build_end_scroll_texts()
        self.end_index = 0
        self.current_scroll_text = self.end_scroll_texts[self.end_index]

    def build_menu(self) -> menu.Menu:
        options = self.quiz.current_question.options
        min_line_width = max([sum([db.font_db.normal_font.get_width(c) for c in option]) for option in options])
        w = math.ceil(min_line_width / 8) + 4
        h = math.ceil(len(options)*13 / 8) + 2
        return menu.Menu((w, h), self.quiz.current_question.options)

    def build_question_scroll_text(self, question: Question) -> text.ScrollText:
        return text.ScrollText(
            text.TextBuilder()
            .set_shadow(True)
            .set_color(text.WHITE)
            .write(question.question)
            .build()
        )

    def build_description_scroll_texts(self) -> list[text.ScrollText]:
        res = []
        for page in self.quiz.nature_descriptions:
            res.append(text.ScrollText(
                text.TextBuilder()
                .set_shadow(True)
                .set_color(text.WHITE)
                .write(page)
                .build()
            ))
        return res

    def build_leader_scroll_text(self) -> text.ScrollText:
        return text.ScrollText(
            text.TextBuilder()
            .set_shadow(True)
            .set_color(text.WHITE)
            .write(f"Will be a ")
            .set_color(text.LIME)
            .write(self.quiz.leader.name)
            .set_color(text.WHITE)
            .write("!")
            .build()
        )

    def build_partner_scroll_texts(self) -> list[text.ScrollText]:
        return [
            text.ScrollText(
                text.TextBuilder()
                .set_shadow(True)
                .set_color(text.WHITE)
                .write("And finally,\nWho will be your partner?")
                .build()
            ),
            text.ScrollText(
                text.TextBuilder()
                .set_shadow(True)
                .set_color(text.WHITE)
                .write("Choose the Pokemon you want for a partner.")
                .build()
            ),
            None
        ]

    def build_end_scroll_texts(self) -> list[text.ScrollText]:
        msgs = [
            "Ok! That's it! You're all ready to go!",
            "You're off to the world of Pokemon!",
            "Be strong! Stay smart! And be victorious!",
        ]
        return [
            text.ScrollText(
                text.TextBuilder()
                .set_shadow(True)
                .set_color(text.WHITE)
                .write(msg)
                .build()
            )
            for msg in msgs
        ]

    def process_input(self, input_stream: InputStream):
        if self.in_transition:
            return
        if self.in_quiz:
            self.process_input_quiz(input_stream)
        elif self.in_description:
            self.process_input_description(input_stream)
        elif self.in_leader:
            self.process_input_leader(input_stream)
        elif self.in_partner:
            self.process_input_partner(input_stream)
        elif self.in_end:
            self.process_input_end(input_stream)

    def process_input_quiz(self, input_stream: InputStream):
        self.current_option_menu.process_input(input_stream)
        if input_stream.keyboard.is_pressed(settings.get_key(Action.INTERACT)) and self.current_scroll_text.is_done:
            selected = self.current_option_menu.pointer
            self.quiz.update_score(selected)
            self.quiz.next_question()
            if self.quiz.current_question is None:
                self.in_quiz = False
                self.current_option_menu = None
                self.init_description()
            else:
                self.current_option_menu = self.build_menu()
                self.current_scroll_text = self.build_question_scroll_text(self.quiz.current_question)

    def process_input_description(self, input_stream: InputStream):
        if input_stream.keyboard.is_pressed(settings.get_key(Action.INTERACT)) and self.current_scroll_text.is_done:
            if 0 <= self.description_index < len(self.description_scroll_texts) - 1:
                self.description_index += 1
                self.current_scroll_text = self.description_scroll_texts[self.description_index]
            else:
                self.in_description = False
                self.init_leader()

    def process_input_leader(self, input_stream: InputStream):
        if input_stream.keyboard.is_pressed(settings.get_key(Action.INTERACT)) and self.current_scroll_text.is_done:
            self.in_leader = False
            self.init_partner()
    
    def process_input_partner(self, input_stream: InputStream):
        if not self.current_scroll_text.is_done:
            return
        if self.partner_index == 1:
            self.partner_menu.process_input(input_stream)
            for key in [settings.get_key(Action.DOWN), settings.get_key(Action.UP), settings.get_key(Action.RIGHT), settings.get_key(Action.LEFT)]:
                if input_stream.keyboard.is_pressed(key):
                    self.partner_portrait_normal_time = self.NORMAL_PORTRAIT_TIME
                    self.partner_emotion = PortraitEmotion.NORMAL
        elif self.partner_index == 2:
            self.current_option_menu.process_input(input_stream)
        if input_stream.keyboard.is_pressed(settings.get_key(Action.INTERACT)):
            if self.partner_index == 0:
                self.partner_index += 1
                self.current_scroll_text = self.partner_scroll_texts[self.partner_index]
            elif self.partner_index == 1:
                self.partner = self.partner_menu.get_selection()
                self.partner_index += 1
                self.partner_scroll_texts[2] = text.ScrollText(
                    text.TextBuilder()
                    .set_shadow(True)
                    .set_color(text.WHITE)
                    .write("Is ")
                    .set_color(text.LIME)
                    .write(self.partner.name)
                    .set_color(text.WHITE)
                    .write(" who you want?")
                    .build()
                )
                self.current_scroll_text = self.partner_scroll_texts[self.partner_index]
                self.current_option_menu = menu.Menu((7, 6), ["Yes.", "No."])
            else:
                if self.current_option_menu.pointer == 0:
                    self.in_partner = False
                    self.init_end()
                else:
                    self.partner_index -= 1
                    self.current_scroll_text = self.partner_scroll_texts[self.partner_index]
                    self.current_scroll_text.t = 0

    def process_input_end(self, input_stream: InputStream):
        if input_stream.keyboard.is_pressed(settings.get_key(Action.INTERACT)) and self.current_scroll_text.is_done:
            if 0 <= self.end_index < len(self.end_scroll_texts) - 1:
                self.end_index += 1
                self.current_scroll_text = self.end_scroll_texts[self.end_index]
            else:
                self.in_end = False
                self.next_scene = self.get_next_scene()

    def update(self):
        super().update()
        self.update_bg()
        self.current_scroll_text.update()
        if self.in_quiz:
            self.current_option_menu.update()
        elif self.in_partner:
            self.update_partner()

    def update_partner(self):
        self.partner_menu.update()
        if self.partner_index == 0:
            return
        if self.partner_index == 1 and not self.current_scroll_text.is_done:
            return
        if self.partner_portrait_normal_time > 0:
            self.partner_portrait_normal_time -= 1
            if self.partner_portrait_normal_time == 0:
                self.partner_emotion = PortraitEmotion.HAPPY

    def update_bg(self):
        self.bg_t += 1
        if self.bg_t % 8 == 0:
            self.frame_index += 1
            self.frame_index %= len(self.frames)
            self.lower_bg.set_palette(self.frames[self.frame_index])
            self.higher_bg.set_palette(self.frames[self.frame_index])
        if self.bg_t % 2 == 0:
            self.lower_x += 1
            if self.lower_x == self.lower_bg.get_width():
                self.lower_x = 0
            self.higher_x -= 1
            if self.higher_x == -self.higher_bg.get_width():
                self.higher_x = 0

    def render(self) -> pygame.Surface:
        surface = self.render_bg()
        if self.in_quiz:
            surface.blit(self.render_question(), (0, 0))
        elif self.in_description:
            surface.blit(self.render_description(), (0, 0))
        elif self.in_leader:
            surface.blit(self.render_leader(), (0, 0))
        elif self.in_partner:
            surface.blit(self.render_partner(), (0, 0))
        elif self.in_end:
            surface.blit(self.render_end(), (0, 0))
        surface.set_alpha(self.alpha)
        return surface

    def render_question(self) -> pygame.Surface:
        surface = pygame.Surface(constants.DISPLAY_SIZE, pygame.SRCALPHA)
        surface.blit(self.frame, (8, 128))
        text_pos = pygame.Vector2(8, 128) + (12, 10)
        surface.blit(self.current_scroll_text.render(), text_pos)
        if self.current_scroll_text.is_done:
            menu_surface = self.current_option_menu.render()
            rect = menu_surface.get_rect(bottomright=(248, 128))
            surface.blit(menu_surface, rect.topleft)
        return surface
    
    def render_description(self) -> pygame.Surface:
        surface = pygame.Surface(constants.DISPLAY_SIZE, pygame.SRCALPHA)
        surface.blit(self.frame, (8, 128))
        text_pos = pygame.Vector2(8, 128) + (12, 10)
        surface.blit(self.current_scroll_text.render(), text_pos)
        return surface

    def render_leader(self) -> pygame.Surface:
        surface = pygame.Surface(constants.DISPLAY_SIZE, pygame.SRCALPHA)
        surface.blit(self.frame, (8, 128))
        text_surface = self.current_scroll_text.render()
        rect = text_surface.get_rect(centerx=surface.get_rect().centerx, y=150)
        surface.blit(text_surface, rect.topleft)
        surface.blit(self.portrait_frame, (104, 32))
        surface.blit(self.leader_portrait.get_portrait(PortraitEmotion.HAPPY), (112, 40))
        return surface

    def render_partner(self) -> pygame.Surface:
        surface = pygame.Surface(constants.DISPLAY_SIZE, pygame.SRCALPHA)
        surface.blit(self.frame, (8, 128))
        text_pos = pygame.Vector2(8, 128) + (12, 10)
        surface.blit(self.current_scroll_text.render(), text_pos)
        if self.partner_index == 1 and self.current_scroll_text.is_done:
            surface.blit(self.partner_menu.render(), (8, 8))
            surface.blit(self.portrait_frame, (120, 32))
            surface.blit(self.partner_menu.get_selected_portrait().get_portrait(self.partner_emotion), (128, 40))
        elif self.partner_index == 2 and self.current_scroll_text.is_done:
            menu_surface = self.current_option_menu.render()
            rect = menu_surface.get_rect(bottomright=(248, 128))
            surface.blit(menu_surface, rect.topleft)
        if self.partner_index == 2:
            surface.blit(self.portrait_frame, (120, 32))
            surface.blit(self.partner_menu.get_selected_portrait().get_portrait(self.partner_emotion), (128, 40))
        return surface

    def render_end(self) -> pygame.Surface:
        return self.render_description()

    def render_bg(self) -> pygame.Surface:
        surface = super().render()
        lower_layer = surface.copy()
        lower_layer.blit(self.lower_bg, (self.lower_x, 0))
        lower_layer.blit(self.lower_bg, (self.lower_x - self.lower_bg.get_width(), 0))
        upper_layer = surface.copy()
        upper_layer.blit(self.higher_bg, (self.higher_x, 0))
        upper_layer.blit(self.higher_bg, (self.higher_x + self.higher_bg.get_width(), 0))
        surface.blit(pygame.transform.average_surfaces((lower_layer, upper_layer)), (0, 0))
        return surface

    def get_next_scene(self):
        leader = pokemon.Pokemon(app.pokemon.pokemon_builder.PokemonBuilder(self.quiz.leader.poke_id).build_level(5))
        partner = pokemon.Pokemon(app.pokemon.pokemon_builder.PokemonBuilder(self.partner.poke_id).build_level(5))
        return StartGroundScene(0, Party([leader, partner]))
