import os
from app.common.constants import SOUND_DIRECTORY
import app.db.database as db


base_dir = os.path.join(SOUND_DIRECTORY, "music")
_cursor = db.main_db.cursor()


def load(bgm: int) -> str:
    try:
        name = _cursor.execute(
            "SELECT name FROM music WHERE music_id == ?", (bgm,)
        ).fetchone()[0]
    except Exception as e:
        print(e)
        name = "Random Dungeon 1"
    return os.path.join(base_dir, f"{name}.mp3")
