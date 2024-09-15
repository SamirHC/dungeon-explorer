import app.db.database as db
from app.quiz.questions import Question
from app.quiz.nature import Nature


cursor = db.main_db.cursor()


def get_questions() -> list[Question]:
    return [
        get_question_by_id(qid[0])
        for qid in cursor.execute("SELECT id FROM quiz_questions").fetchall()
    ]


def get_question_by_id(question_id: int) -> Question:
    q = Question(
        cursor.execute(
            "SELECT question FROM quiz_questions WHERE id = ?", (question_id,)
        ).fetchone()[0]
    )
    answer_ids = cursor.execute(
        "SELECT id, answer FROM quiz_answers "
        "WHERE question_id = ?"
        "ORDER BY menu_index",
        (question_id,),
    ).fetchall()
    for answer_id, answer in answer_ids:
        result = cursor.execute(
            "SELECT nature, score FROM quiz_answer_effects WHERE answer_id = ?",
            (answer_id,),
        ).fetchall()
        q.add_option(answer, [(Nature[p[0]], p[1]) for p in result])
    return q
