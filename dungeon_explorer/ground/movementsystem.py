import pygame

from dungeon_explorer.common import inputstream, direction
from dungeon_explorer.ground import ground
from dungeon_explorer.pokemon import party, pokemon


WALK_SPEED = 2
SPRINT_SPEED = 4


class MovementSystem:
    def __init__(self, ground: ground.Ground):
        self.ground = ground
        self.moving: list[pokemon.Pokemon] = []
        self.movement_speed = WALK_SPEED
        self.intention: direction.Direction = None

    @property
    def party(self) -> party.Party:
        return self.ground.party
    
    def is_occupied_by_npc(self, position: tuple[int, int]):
        x, y = position
        for p in self.ground.npcs:
            if abs(p.x - x) < 16 and abs(p.y - y) < 8:
                return True
        return False

    def can_move(self, p: pokemon.Pokemon, d: direction.Direction) -> bool:
        new_pos = p.x + d.x, p.y + d.y
        if not self.ground.ground_data.bg.get_rect().collidepoint(new_pos):
            return False
        if self.is_occupied_by_npc(new_pos):
            return False
        return not self.ground.is_collision(new_pos)
        

    def process_input(self, input_stream: inputstream.InputStream):
        kb = input_stream.keyboard
        dx = 0
        dy = 0
        self.intention = None
        if kb.is_pressed(pygame.K_LCTRL) or kb.is_held(pygame.K_LCTRL):
            self.movement_speed = SPRINT_SPEED
        else:
            self.movement_speed = WALK_SPEED
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
        self.intention = d

    def update(self):
        if self.intention is not None:
            self.party.leader.direction = self.intention
            for _ in range(self.movement_speed):
                if self.can_move(self.party.leader, self.party.leader.direction):
                    self.moving.append(self.party.leader)
                    for p1, p2 in zip(self.party.members, self.party.members[1:]):
                        p2.face_target(p1.tracks[-1])
                        self.moving.append(p2)

        for p in self.moving:
            p.animation_id = p.walk_animation_id()
            if self.can_move(p, p.direction):
                p.move()
        self.moving.clear()