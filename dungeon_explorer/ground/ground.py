import dataclasses
import pygame
from dungeon_explorer.pokemon import pokemon, party


@dataclasses.dataclass
class GroundData:
    bg: pygame.Surface
    collision: set[tuple[int, int]]
    spawns: list[tuple[int, int]]
    npcs: list[pokemon.Pokemon]


class Ground:
    def __init__(self, ground_data: GroundData, party: party.Party):
        self.ground_data = ground_data
        self.party = party
        self.spawned: list[pokemon.Pokemon] = []
        self.npcs: list[pokemon.Pokemon] = []
        self.spawn_party(party)
        for p in self.ground_data.npcs:
            self.spawn_npc(p, (400, 300))

    def spawn_party(self, party: party.Party):
        for p, pos in zip(party, self.ground_data.spawns):
            p.spawn(pos)
            p.tracks = [p.position] * 24
            self.spawned.append(p)

    def spawn_npc(self, npc: pokemon.Pokemon, position: tuple[int, int]):
        npc.spawn(position)
        self.spawned.append(npc)
        self.npcs.append(npc)

    def render(self) -> pygame.Surface:
        surface = self.ground_data.bg.copy()
        for p in sorted(self.spawned, key=lambda p: p.y):
            sprite_surface = p.render()
            sprite_rect = sprite_surface.get_rect(center=p.position)
            surface.blit(sprite_surface, sprite_rect)
        return surface