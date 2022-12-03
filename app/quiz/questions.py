import os
import xml.etree.ElementTree as ET

from app.quiz.nature import Nature


class Question:
    def __init__(self, question: str):
        self.question = question
        self.options: list[str] = []
        self.results: list[list[tuple[Nature, int]]] = []

    def add_option(self, option: str, result: list[tuple[Nature, int]]):
        self.options.append(option)
        self.results.append(result)

def load_questions() -> list[Question]:
    file = os.path.join("data", "gamedata", "quiz", "questions.xml")
    root = ET.parse(file).getroot()
    questions = []
    for question_element in root.findall("Question"):
        q = Question(question_element.get("name"))
        for option_element in question_element.findall("Option"):
            name = option_element.get("name")
            result = [(Nature[ef.get("nature")], int(ef.get("score"))) for ef in option_element.findall("Effect")]
            q.add_option(name, result)
        questions.append(q)
    
    return questions
