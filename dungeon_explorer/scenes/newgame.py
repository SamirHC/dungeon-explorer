import math
import os
import random
import xml.etree.ElementTree as ET

import pygame
import pygame.image
import pygame.transform

from dungeon_explorer.common import inputstream, constants, text, textbox, menu
from dungeon_explorer.pokemon import party, pokemon, pokemondata
from dungeon_explorer.quiz import nature, questions
from dungeon_explorer.scenes import scene, dungeon


class NewGameScene(scene.Scene):
    def __init__(self):
        super().__init__()
        self.scroll_texts = [
            text.ScrollText("Welcome!"),
            text.ScrollText("This is the portal that leads to the\nworld inhabited only by Pokemon.", text.Font.CENTER_ALIGN),
            text.ScrollText("Beyond this gateway, many new\nadventures and fresh experiences\nawait your arrival!", text.Font.CENTER_ALIGN),
            text.ScrollText("Before you depart for adventure,\nyou must answer some questions.", text.Font.CENTER_ALIGN),
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
                self.next_scene = QuizScene()

    def update(self):
        self.current_text.update()

    def render(self) -> pygame.Surface:
        surface = pygame.Surface(constants.DISPLAY_SIZE, pygame.SRCALPHA)
        surface.fill(constants.BLACK)
        rect = self.current_text.empty_surface.get_rect(centerx=surface.get_rect().centerx, y=80)
        surface.blit(self.current_text.render(), rect.topleft)
        return surface


class QuizScene(scene.Scene):
    def __init__(self):
        super().__init__()
        self.lower_bg = pygame.image.load(os.path.join("assets", "images", "bg", "quiz", "lower.png"))
        self.lower_x = 0
        self.higher_bg = pygame.image.load(os.path.join("assets", "images", "bg", "quiz", "higher.png"))
        self.higher_x = 0
        anim_root = ET.parse(os.path.join("assets", "images", "bg", "quiz", "palette_data.xml")).getroot()
        self.frames = [[pygame.Color(f"#{color.text}") for color in frame.findall("Color")] for frame in anim_root.findall("Frame")]
        self.t = 0
        self.frame_index = 0

        self.questions = self.get_questions()
        self.score = {n: 0 for n in nature.Nature}
        self.has_played = False
        self.gender = False
        self.q_index = 0
        self.quiz_ended = False
        self.current_scroll_text = text.ScrollText(self.current_question.question)
        self.current_option_menu = self.build_menu()

        self.scroll_text_queue = ["Thank you for answering all those questions."]
        self.st_index = 0

        self.question_box = textbox.Frame((30, 7), 255)

    def get_questions(self) -> list[questions.Question]:
        all_questions = questions.load_questions()
        played_question = all_questions.pop(0)
        gender_question = all_questions.pop()
        nature_questions = random.sample(all_questions, 10)
        return [played_question] + nature_questions + [gender_question]

    @property
    def current_question(self) -> questions.Question:
        return self.questions[self.q_index]

    def build_menu(self):
        options = self.current_question.options
        min_line_width = max([sum([text.normal_font.get_width(c) for c in option]) for option in options])
        w = math.ceil(min_line_width / 8) + 4
        h = math.ceil(len(options)*13 / 8) + 2
        return menu.Menu((w, h), self.current_question.options)

    def next_question(self):
        self.q_index += 1
        self.current_scroll_text = text.ScrollText(self.current_question.question)
        self.current_option_menu = self.build_menu()

    def get_nature_element(self, nature: nature.Nature):
        file = os.path.join("data", "gamedata", "quiz", "nature.xml")
        root = ET.parse(file).getroot()
        for node in root.findall("Nature"):
            if node.get("name") == nature.name:
                return node

    def process_input(self, input_stream: inputstream.InputStream):
        self.current_option_menu.process_input(input_stream)
        if input_stream.keyboard.is_pressed(pygame.K_RETURN):
            if not self.quiz_ended:
                selected = self.current_option_menu.pointer
                for nat, val in self.current_question.results[selected]:
                    self.score[nat] += val
                if self.q_index == 0:
                    self.has_played = selected == 0
                if self.q_index == len(self.questions) - 1:
                    self.gender = "Male" if selected == 0 else "Female"
                    self.quiz_ended = True
                    final_nature = max(self.score, key=self.score.get)
                    nature_node = self.get_nature_element(final_nature)
                    self.scroll_text_queue += [n.text for n in nature_node.find("Description").findall("Page")]
                    self.current_scroll_text = text.ScrollText(self.scroll_text_queue[self.st_index])
                    poke_id = pokemondata.get_poke_id_by_pokedex(int(nature_node.find(self.gender).text))
                    self.user_pokemon = pokemon.EnemyPokemon(poke_id, 5)
                else:
                    self.next_question()
                return
            else:
                if self.st_index < len(self.scroll_text_queue) - 1:
                    self.st_index += 1
                    self.current_scroll_text = text.ScrollText(self.scroll_text_queue[self.st_index])
                elif self.st_index == len(self.scroll_text_queue) - 1:
                    self.current_scroll_text = text.ScrollText(f"Will be a {self.user_pokemon.name}!")
            
            #entry_party = party.Party("0")
            #entry_party.add("3")
            #self.next_scene = dungeon.StartDungeonScene("14", entry_party)
        
    def update(self):
        self.update_bg()
        self.current_scroll_text.update()
        if not self.quiz_ended:
            self.current_option_menu.update()

    def update_bg(self):
        self.t += 1
        if self.t % 8 == 0:
            self.frame_index += 1
            self.frame_index %= len(self.frames)
            self.lower_bg.set_palette(self.frames[self.frame_index])
            self.higher_bg.set_palette(self.frames[self.frame_index])
        if self.t % 2 == 0:
            self.lower_x += 1
            if self.lower_x == self.lower_bg.get_width():
                self.lower_x = 0
            self.higher_x -= 1
            if self.higher_x == -self.higher_bg.get_width():
                self.higher_x = 0

    def render(self) -> pygame.Surface:
        surface = self.render_bg()
        surface.blit(self.question_box, (8, 128))
        text_pos = pygame.Vector2(8, 128) + (12, 10)
        surface.blit(self.current_scroll_text.render(), text_pos)
        if not self.quiz_ended:
            menu_surface = self.current_option_menu.render()
            rect = menu_surface.get_rect(bottomright=(248, 128))
            surface.blit(menu_surface, rect.topleft)
        return surface

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