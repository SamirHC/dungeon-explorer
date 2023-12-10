from collections import Counter
import random
import os
import xml.etree.ElementTree as ET

from app.quiz import questions
from app.quiz.nature import Nature
import app.db.database as db

from app.common.constants import GAMEDATA_DIRECTORY


class Quiz:
    def __init__(self):
        self.questions = questions.load_questions()
        self.played_question = self.questions.pop(0)
        self.gender_question = self.questions.pop()
        random.shuffle(self.questions)

        self.score = Counter()
        self.questions_answered = 0

        self.current_question = self.played_question

    def update_score(self, selection: int):
        for nat, val in self.current_question.results[selection]:
            self.score[nat] += val
        if self.current_question is self.played_question:
            self.has_played = selection == 0
        elif self.current_question is self.gender_question:
            self.gender = "Male" if (selection == 0) else "Female"

    def next_question(self):
        self.questions_answered += 1
        if self.current_question is self.gender_question:
            self.current_question = None
            self.get_result()
            return
        if self.questions_answered > 8:
            first, second = self.score.most_common(2)
            if first[1] > second[1]:
                self.current_question = self.gender_question
                return
        self.current_question = self.questions.pop()

    def get_result(self):
        self.nature: Nature = self.score.most_common(1)[0][0]
        file = os.path.join(GAMEDATA_DIRECTORY, "quiz", "nature.xml")
        root = ET.parse(file).getroot()
        for node in root.findall("Nature"):
            if node.get("name") == self.nature.name:
                nature_node = node
                break
        self.nature_descriptions = [
            page.text for page in nature_node.find("Description").findall("Page")
        ]
        leader_id = db.genericpokemon_db.get_poke_id_by_pokedex(
            int(nature_node.find(self.gender).text)
        )
        self.leader = db.genericpokemon_db[leader_id]
