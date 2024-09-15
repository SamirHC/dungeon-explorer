from collections import Counter

from app.common.constants import RNG as random
from app.pokemon.gender import Gender
from app.quiz.nature import Nature
import app.db.database as db
import app.db.base_pokemon as base_pokemon_db
import app.db.quiz_question as quiz_question_db


class Quiz:
    def __init__(self):
        self.questions = quiz_question_db.get_questions()
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
            self.gender = Gender.MALE if (selection == 0) else Gender.FEMALE

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
        
        cursor = db.main_db.cursor()
        self.nature_descriptions = [r[0] for r in cursor.execute(
            "SELECT description FROM nature_descriptions "
            "WHERE nature_id = ? "
            "ORDER BY page",
            (self.nature.value, )
        ).fetchall()]
        pokedex = cursor.execute(
            f"SELECT {self.gender.name.lower()} FROM natures "
            "WHERE id = ?",
            (self.nature.value, )
        ).fetchone()[0]
        
        leader_id = base_pokemon_db.get_poke_id_by_pokedex(pokedex)
        self.leader = base_pokemon_db.load(leader_id)
