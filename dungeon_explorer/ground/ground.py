import dataclasses
import pygame
from dungeon_explorer.pokemon import pokemon, party


@dataclasses.dataclass
class GroundData:
    bg: pygame.Surface
    collision: set[tuple[int, int]]
    spawn: tuple[int, int]


class Ground:
    def __init__(self, ground_data: GroundData, party: party.Party):
        self.ground_data = ground_data
        self.party = party
        self.spawned = []
        self.spawn_party(party)

    def spawn_party(self, party: party.Party):
        for p in party:
            self.spawn_npc(p, self.ground_data.spawn)

    def spawn_npc(self, npc: pokemon.Pokemon, position: tuple[int, int]):
        npc.spawn(position)
        self.spawned.append(npc)

    def render(self) -> pygame.Surface:
        return self.ground_data.bg.copy()