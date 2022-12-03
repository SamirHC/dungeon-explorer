import os

class MusicDatabase:
    def __init__(self):
        self.base_dir = os.path.join("assets", "sound", "music")
        self.loaded = {}
        self.bgm_names = {
            -2: "Welcome To the World of Pokemon!",
            -1: "Top Menu Theme",
            0: "Treasure Town",
            1: "Beach Cave",
            2: "Drenched Bluff",
            3: "Mt. Bristle",
            4: "Waterfall Cave",
            5: "Apple Woods",
            6: "Craggy Coast",
            7: "Cave and Side Path",
            8: "Mt. Horn",
            9: "Foggy Forest",
            10: "Steam Cave",
            11: "Upper Steam Cave",
            12: "Amp Plains",
            13: "Far Amp Plains",
            14: "Northern Desert",
            15: "Quicksand Cave",
            16: "Quicksand Pit",
            17: "Crystal Cave",
            18: "Crystal Crossing",
            19: "Chasm Cave",
            20: "Dark Hill",
            21: "Sealed Ruin",
            22: "Sealed Ruin Pit",
            23: "Dusk Forest",
            24: "Deep Dusk Forest",
            25: "Treeshroud Forest",
            26: "Brine Cave",
            27: "Lower Brine Cave",
            28: "Hidden Land",
            29: "Hidden Highland",
            30: "Temporal Tower",
            31: "Temporal Spire",
            32: "Mystifying Forest",
            33: "Blizzard Island Rescue Team Medley",
            34: "Surrounded Sea",
            35: "Miracle Sea",
            36: "Aegis Cave",
            37: "Concealed Ruins",
            38: "Mt. Travail",
            39: "In The Nightmare",
            42: "Dark Crater",
            43: "Deep Dark Crater",
            117: "Marowak Dojo",
        }

    def __getitem__(self, bgm: int) -> str:
        if bgm not in self.loaded:
            self.load(bgm)
        return self.loaded[bgm]

    def load(self, bgm: int):
        music_name = self.bgm_names.get(bgm, "Treasure Town")
        file_name = os.path.join("assets", "sound", "music", f"{music_name}.mp3")
        self.loaded[bgm] = file_name
