from enum import Enum
import os

import pygame
import pygame.image

from app.common.constants import IMAGES_DIRECTORY


class Trap(Enum):
    UNUSED = "UNUSED"
    MUD_TRAP = "MUD_TRAP"
    STICKY_TRAP = "STICKY_TRAP"
    GRIMY_TRAP = "GRIMY_TRAP"
    SUMMON_TRAP = "SUMMON_TRAP"
    PITFALL_TRAP = "PITFALL_TRAP"
    WARP_TRAP = "WARP_TRAP"
    GUST_TRAP = "GUST_TRAP"
    SPIN_TRAP = "SPIN_TRAP"
    SLUMBER_TRAP = "SLUMBER_TRAP"
    SLOW_TRAP = "SLOW_TRAP"
    SEAL_TRAP = "SEAL_TRAP"
    POISON_TRAP = "POISON_TRAP"
    SELFDESTRUCT_TRAP = "SELFDESTRUCT_TRAP"
    EXPLOSION_TRAP = "EXPLOSION_TRAP"
    PP_ZERO_TRAP = "PP_ZERO_TRAP"
    CHESTNUT_TRAP = "CHESTNUT_TRAP"
    WONDER_TILE = "WONDER_TILE"
    POKEMON_TRAP = "POKEMON_TRAP"
    SPIKED_TILE = "SPIKED_TILE"
    STEALTH_ROCK = "STEALTH_ROCK"
    TOXIC_SPIKES = "TOXIC_SPIKES"
    TRIP_TRAP = "TRIP_TRAP"
    RANDOM_TRAP = "RANDOM_TRAP"
    GRUDGE_TRAP = "GRUDGE_TRAP"


class TrapTileset:
    def __init__(self):
        base_dir = os.path.join(IMAGES_DIRECTORY, "traps")
        self.trapset = {
            t: pygame.image.load(os.path.join(base_dir, f"{t.value}.png")) for t in Trap
        }

    def __getitem__(self, trap: Trap) -> pygame.Surface:
        return self.trapset[trap]


trap_tileset = TrapTileset()
