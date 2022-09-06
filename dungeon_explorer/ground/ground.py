from __future__ import annotations
import pygame
from dungeon_explorer.pokemon import pokemon, party
from dungeon_explorer.ground import grounddata


class Ground:
    def __init__(self, ground_scene_data: grounddata.GroundSceneData, party: party.Party):
        self.ground_scene_data = ground_scene_data
        self.location_id = ground_scene_data.location
        self.party = party
        self.spawned: list[pokemon.Pokemon] = []
        self.npcs: list[pokemon.Pokemon] = []
        self.spawn_party(party)
        for p in self.ground_data.npcs:
            self.spawn_npc(p, (400, 300))
        self.next_ground = None
        self.menu = None

    @property
    def ground_data(self) -> grounddata.GroundData:
        return self.ground_scene_data.ground_data

    @property
    def width(self) -> int:
        return self.ground_data.ground_map.lower_bg.get_width()

    @property
    def height(self) -> int:
        return self.ground_data.ground_map.lower_bg.get_height()

    def spawn_party(self, party: party.Party):
        for p, pos in zip(party, self.ground_data.spawns):
            p.spawn(pos)
            p.tracks = [p.position] * 24
            self.spawned.append(p)

    def spawn_npc(self, npc: pokemon.Pokemon, position: tuple[int, int]):
        npc.spawn(position)
        self.spawned.append(npc)
        self.npcs.append(npc)

    def is_collision(self, pos: tuple[int, int]) -> bool:
        x, y = pos
        tile_pos = x // 8, y // 8
        return self.ground_data.ground_map.collision[tile_pos]

    def process_triggers(self, pos: tuple[int, int]) -> int:
        x, y = pos
        tile_pos = x // 8, y // 8
        self.menu = None
        for trigger_type, rect, id in self.ground_data.event_triggers:
            if rect.collidepoint(tile_pos):
                if trigger_type == "next_scene":
                    self.next_ground = id
                elif trigger_type == "destination_menu":
                    self.menu = trigger_type

    def update(self):
        self.ground_data.ground_map.update()
        self.process_triggers(self.party.leader.position)

    def render(self) -> pygame.Surface:
        surface = self.ground_data.ground_map.render().convert_alpha()

        # TRIGGER COLLISION MAP
        for _, rect, _ in self.ground_data.event_triggers:
            x, y = rect.x * 8, rect.y * 8
            w, h = rect.w * 8, rect.h * 8
            collision_surf = pygame.Surface((w, h), pygame.SRCALPHA)
            collision_surf.fill((0, 0, 255, 128))
            surface.blit(collision_surf, (x, y))
        ####
    
        for p in sorted(self.spawned, key=lambda p: p.y):
            sprite_surface = p.render()
            sprite_rect = sprite_surface.get_rect(center=p.position)
            surface.blit(sprite_surface, sprite_rect)
        return surface