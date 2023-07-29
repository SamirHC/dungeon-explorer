import pygame

from app.common import settings, inputstream, direction
from app.ground import ground
from app.pokemon import party, pokemon


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
        new_x, new_y = p.x + d.x, p.y + d.y
        hitbox = pygame.Rect(new_x - 8, new_y - 4, 15, 7)
        tile_top = hitbox.top // 8
        tile_left = hitbox.left // 8
        tile_bottom = hitbox.bottom // 8
        tile_right = hitbox.right // 8
        for x in range(tile_left, tile_right+1):
            for y in range(tile_top, tile_bottom+1):
                new_pos = x * 8, y * 8
                if self.is_occupied_by_npc(new_pos):
                    return False
                if self.ground.is_collision(new_pos):
                    return False
        return True
        
    def process_input(self, input_stream: inputstream.InputStream):
        kb = input_stream.keyboard
        dx = 0
        dy = 0
        self.intention = None
        if kb.is_pressed(settings.get_run_key()) or kb.is_held(settings.get_run_key()):
            self.movement_speed = SPRINT_SPEED
        else:
            self.movement_speed = WALK_SPEED
        if kb.is_pressed(settings.get_walk_north_key()) or kb.is_held(settings.get_walk_north_key()):
            dy -= 1
        if kb.is_pressed(settings.get_walk_west_key()) or kb.is_held(settings.get_walk_west_key()):
            dx -= 1
        if kb.is_pressed(settings.get_walk_south_key()) or kb.is_held(settings.get_walk_south_key()):
            dy += 1
        if kb.is_pressed(settings.get_walk_east_key()) or kb.is_held(settings.get_walk_east_key()):
            dx += 1

        if not (dx or dy):
            return
        
        d = direction.Direction((dx, dy))
        self.intention = d

    def update(self):
        if self.intention is None:
            return

        self.party.leader.direction = self.intention
        self.party.leader.animation_id = self.party.leader.walk_animation_id()
        for _ in range(self.movement_speed):
            if self.can_move(self.party.leader, self.intention):
                self.party.leader.move()
            elif self.intention.is_diagonal():
                acw = self.intention.anticlockwise()
                cw = self.intention.clockwise()
                if self.can_move(self.party.leader, acw):
                    self.party.leader.move(acw)
                elif self.can_move(self.party.leader, cw):
                    self.party.leader.move(cw)
                else:
                    break
            else:
                break
            for p1, p2 in zip(self.party.members, self.party.members[1:]):
                p2.face_target(p1.tracks[-1])
                p2.animation_id = p2.walk_animation_id()
                p2.move()

        #for p in self.moving:
        #    p.animation_id = p.walk_animation_id()
        #    if self.can_move(p, p.direction):
        #        p.move()

        self.moving.clear()