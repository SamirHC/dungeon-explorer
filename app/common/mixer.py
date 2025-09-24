import pygame

from app.common import settings
import app.db.music as music_db


class SilentMixer:
    def __init__(self):
        self.num_channels = 0
        self.music = self.SilentMusic()

    # --- Top-level mixer functions ---
    def init(self, *_, **__): pass
    def quit(self): pass

    def set_num_channels(self, n: int):
        self.num_channels = n

    def get_num_channels(self) -> int:
        return self.num_channels

    def Sound(self, *_, **__):
        return self.SilentSound()

    def Channel(self, *_args, **_kwargs):
        return self.SilentChannel()

    # --- Inner stub classes ---

    class SilentSound:
        def play(self, *_, **__): pass
        def stop(self): pass
        def fadeout(self, *_): pass
        def set_volume(self, *_): pass
        def get_volume(self): return 0.0
        def get_length(self): return 0.0

    class SilentChannel:
        def play(self, *_, **__): pass
        def stop(self): pass
        def pause(self): pass
        def unpause(self): pass
        def fadeout(self, *_): pass
        def set_volume(self, *_): pass
        def get_volume(self): return 0.0
        def get_busy(self): return False

    class SilentMusic:
        def load(self, *_): pass
        def play(self, *_, **__): pass
        def stop(self): pass
        def pause(self): pass
        def unpause(self): pass
        def rewind(self): pass
        def fadeout(self, *_): pass
        def set_volume(self, *_): pass
        def get_volume(self): return 0.0
        def get_busy(self): return False


try:
    pygame.mixer.init()
except pygame.error as e:
    print(f"[Audio disabled] {e}")
    pygame.mixer = SilentMixer()


pygame.mixer.set_num_channels(8)
misc_sfx_channel = pygame.mixer.Channel(1)

pygame.mixer.music.set_volume(settings.get_bgm())

current_bgm = None


def set_bgm(new_bgm: int):
    global current_bgm
    if current_bgm is new_bgm:
        return
    if current_bgm is not None:
        pygame.mixer.music.fadeout(500)
    current_bgm = new_bgm
    if new_bgm is not None:
        pygame.mixer.music.load(music_db.load(new_bgm))
        pygame.mixer.music.play(-1)
