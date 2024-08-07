from __future__ import annotations
import pygame
from app.pokemon.party import Party
from app.pokemon import pokemon
from app.ground.ground_data import GroundSceneData, GroundData
from app.gui import shadow


class Ground:
    def __init__(self, ground_scene_data: GroundSceneData, party: Party):
        self.ground_scene_data = ground_scene_data
        self.location_id = ground_scene_data.location
        self.party = party
        self.spawned: list[pokemon.Pokemon] = []
        self.npcs: list[pokemon.Pokemon] = []
        self.spawn_party(party)
        for p in self.ground_data.npcs:
            self.spawn_npc(p, (400, 300))  # TODO: spawn position
        self.next_ground = None
        self.trigger = None
        self.menu = None
        self.render_toggle = True

    def reload(self):
        self.ground_scene_data.reload()

    @property
    def ground_data(self) -> GroundData:
        return self.ground_scene_data.ground_data

    @property
    def width(self) -> int:
        return self.ground_data.ground_map.lower_bg.get_width()

    @property
    def height(self) -> int:
        return self.ground_data.ground_map.lower_bg.get_height()

    def spawn_party(self, party: Party):
        for p in party:
            p.spawn(p.position)
            p.tracks = [p.position] * 24
            self.spawned.append(p)

    def spawn_npc(self, npc: pokemon.Pokemon, position: tuple[int, int]):
        npc.spawn(position)
        self.spawned.append(npc)
        self.npcs.append(npc)

    def is_collision(self, pos: tuple[int, int]) -> bool:
        return self.ground_data.ground_map.collision.get_at(pos).a > 0

    def process_triggers(self, pos: tuple[int, int]) -> int:
        x, y = pos
        tile_pos = x // 8, y // 8
        self.menu = None
        self.next_ground = None
        self.trigger = None
        for trigger in self.ground_data.event_triggers:
            rect = trigger.rect
            trigger_type = trigger.event_class
            id = trigger.id
            if rect.collidepoint(tile_pos):
                if trigger_type == "next_scene":
                    self.next_ground = id
                    self.trigger = trigger
                elif trigger_type == "destination_menu":
                    self.menu = trigger_type
                    self.trigger = trigger

    def update(self):
        self.ground_data.ground_map.update()
        self.process_triggers(self.party.leader.position)

    def render(self) -> pygame.Surface:
        surface = self.ground_data.ground_map.render().convert_alpha()

        # TRIGGER COLLISION MAP
        if self.render_toggle:
            for event_trigger in self.ground_data.event_triggers:
                rect = event_trigger.rect
                x, y = rect.x * 8, rect.y * 8
                w, h = rect.w * 8, rect.h * 8
                collision_surf = pygame.Surface((w, h), pygame.SRCALPHA)
                collision_surf.fill((0, 0, 255, 128))
                surface.blit(collision_surf, (x, y))
        ####

        for p in sorted(self.spawned, key=lambda p: p.y):
            sprite_surface = p.render()
            sprite_rect = sprite_surface.get_rect(center=p.position)

            shadow_surface = shadow.get_black_shadow(p.sprite.shadow_size)
            shadow_rect = shadow_surface.get_rect(
                center=pygame.Vector2(sprite_rect.topleft)
                + pygame.Vector2(p.sprite.current_shadow_position)
            )

            surface.blit(shadow_surface, shadow_rect)
            surface.blit(sprite_surface, sprite_rect)
        return surface

    def toggle_render_mode(self):
        self.render_toggle = not self.render_toggle
        self.ground_data.ground_map.render_toggle = self.render_toggle
