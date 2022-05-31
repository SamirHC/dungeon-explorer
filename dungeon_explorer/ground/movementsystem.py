import pygame

from dungeon_explorer.common import inputstream, direction
from dungeon_explorer.ground import ground
from dungeon_explorer.pokemon import party, pokemon


class MovementSystem:
    def __init__(self, ground: ground.Ground):
        self.ground = ground

    @property
    def party(self) -> party.Party:
        return self.ground.party
    
    def is_occupied_by_npc(self, position: tuple[int, int]):
        x, y = position
        for p in self.ground.npcs:
            if p.x // 8 == x and p.y // 8 == y:
                return True
        return False

    def can_move(self, p: pokemon.Pokemon, d: direction.Direction) -> bool:
        new_pos = x, y = p.x + d.x, p.y + d.y
        new_tile_pos = x // 8, y // 8
        if new_tile_pos in self.ground.ground_data.collision:
            return False
        if self.is_occupied_by_npc(new_tile_pos):
            return False
        return self.ground.ground_data.bg.get_rect().collidepoint(new_pos)

    def process_input(self, input_stream: inputstream.InputStream):
        kb = input_stream.keyboard
        dx = 0
        dy = 0
        if kb.is_pressed(pygame.K_w) or kb.is_held(pygame.K_w):
            dy -= 1
        if kb.is_pressed(pygame.K_a) or kb.is_held(pygame.K_a):
            dx -= 1
        if kb.is_pressed(pygame.K_s) or kb.is_held(pygame.K_s):
            dy += 1
        if kb.is_pressed(pygame.K_d) or kb.is_held(pygame.K_d):
            dx += 1

        if not (dx or dy):
            return
        
        d = direction.Direction((dx, dy))
        self.party.leader.direction = d
        self.party.leader.animation_id = self.party.leader.walk_animation_id()
        if self.can_move(self.party.leader, d):
            self.party.leader.move()
            for p1, p2 in zip(self.party.members, self.party.members[1:]):
                p2.animation_id = p2.walk_animation_id()
                p2.face_target(p1.tracks[-1])
                p2.move()
