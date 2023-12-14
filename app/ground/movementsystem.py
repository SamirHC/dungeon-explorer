import pygame

from app.common.action import Action
from app.common.direction import Direction
from app.common.inputstream import InputStream
from app.common import settings
from app.ground import ground
from app.pokemon.party import Party
from app.pokemon.animation_id import AnimationId
from app.pokemon.pokemon import Pokemon


WALK_SPEED = 2
SPRINT_SPEED = 4


class MovementSystem:
    def __init__(self, ground: ground.Ground):
        self.ground = ground
        self.moving: list[Pokemon] = []
        self.movement_speed = WALK_SPEED
        self.intention: Direction = None

    @property
    def party(self) -> Party:
        return self.ground.party

    def is_occupied_by_npc(self, position: tuple[int, int]):
        x, y = position
        for p in self.ground.npcs:
            if abs(p.x - x) < 16 and abs(p.y - y) < 8:
                return True
        return False

    def can_move(self, p: Pokemon, d: Direction) -> bool:
        new_x, new_y = p.x + d.x, p.y + d.y
        hitbox = pygame.Rect(new_x - 8, new_y - 4, 15, 7)
        tile_top = hitbox.top // 8
        tile_left = hitbox.left // 8
        tile_bottom = hitbox.bottom // 8
        tile_right = hitbox.right // 8

        return not any(
            self.is_collision((x * 8, y * 8))
            for x in range(tile_left, tile_right + 1)
            for y in range(tile_top, tile_bottom + 1)
        )

    def is_collision(self, position: tuple[int, int]):
        return self.ground.is_collision(position) or self.is_occupied_by_npc(position)

    def process_input(self, input_stream: InputStream):
        action_dirs = (
            (Action.UP, Direction.NORTH),
            (Action.LEFT, Direction.WEST),
            (Action.DOWN, Direction.SOUTH),
            (Action.RIGHT, Direction.EAST),
        )
        kb = input_stream.keyboard

        self.movement_speed = (
            SPRINT_SPEED if kb.is_down(settings.get_key(Action.RUN)) else WALK_SPEED
        )

        dx = sum(d.x for a, d in action_dirs if kb.is_down(settings.get_key(a)))
        dy = sum(d.y for a, d in action_dirs if kb.is_down(settings.get_key(a)))

        self.intention = Direction((dx, dy)) if dx or dy else None

    def update(self):
        if self.intention is None:
            return

        self.party.leader.direction = self.intention
        self.party.leader.animation_id = AnimationId.WALK
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
                p2.animation_id = AnimationId.WALK
                p2.move()

        self.moving.clear()
