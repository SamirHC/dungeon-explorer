from app.quiz.nature import Nature


class Question:
    def __init__(self, question: str):
        self.question = question

        self.options: list[str] = []
        self.results: list[list[tuple[Nature, int]]] = []

    def add_option(self, option: str, result: list[tuple[Nature, int]]):
        self.options.append(option)
        self.results.append(result)
