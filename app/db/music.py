import os
from app.common.constants import SOUND_DIRECTORY
import app.db.database as db


class MusicDatabase:
    def __init__(self):
        self.base_dir = os.path.join(SOUND_DIRECTORY, "music")
        self.cursor = db.main_db.cursor()

    def __getitem__(self, bgm: int) -> str:
        self.cursor.execute("SELECT name FROM music WHERE music_id == ?", (bgm,))
        name = self.cursor.fetchone()[0]
        return os.path.join(SOUND_DIRECTORY, "music", f"{name}.mp3")
