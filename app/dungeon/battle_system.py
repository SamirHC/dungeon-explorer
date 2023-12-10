import random
from collections import deque

from app.common.action import Action
from app.common.inputstream import InputStream
from app.common import settings
from app.dungeon import target_getter
from app.dungeon.dungeon import Dungeon
from app.events import event
from app.move.move import MoveRange
from app.pokemon.pokemon import Pokemon
import app.db.database as db


class BattleSystem:
    def __init__(self, dungeon: Dungeon, event_queue: deque[event.Event]):
        self.dungeon = dungeon
        self.party = dungeon.party
        self.floor = dungeon.floor
        self.log = dungeon.dungeon_log

        self.current_move = None
        self.attacker: Pokemon = None
        self.defender: Pokemon = None
        self.defender_fainted = False  # To bypass side effects of damaging moves

    # USER
    def process_input(self, input_stream: InputStream) -> bool:
        kb = input_stream.keyboard

        attacker = self.party.leader
        action_index = {
            Action.INTERACT: -1,
        }
        for i in range(len(attacker.moveset)):
            if attacker.moveset.selected[i] and attacker.moveset.can_use(i):
                action_index[Action[f"MOVE_{i + 1}"]] = i

        pressed = [a for a in action_index if kb.is_pressed(settings.get_key(a))]

        success = len(pressed) == 1
        if len(pressed) == 1:        
            self.attacker = attacker
            self.activate(action_index[pressed[0]])
        
        return success

    # TARGETS
    def get_targets(self) -> list[Pokemon]:
        return target_getter.get_targets(self.attacker, self.dungeon, self.current_move.move_range)

    # AI
    def ai_attack(self, p: Pokemon):
        self.attacker = p
        target_getter.set_pokemon(p)
        enemies = target_getter.get_enemies(self.dungeon)
        target_getter.deactivate()
        if enemies:
            target_enemy = min(enemies, key=lambda e: max(abs(e.x - self.attacker.x), abs(e.y - self.attacker.y)))
            if self.floor.can_see(self.attacker.position, target_enemy.position):
                self.attacker.face_target(target_enemy.position)
        if self.ai_activate():
            return True
        self.deactivate()
        return False

    def ai_select_move_index(self) -> int:
        REGULAR_ATTACK_INDEX = -1
        moveset = self.attacker.moveset

        move_indices = [REGULAR_ATTACK_INDEX] + [i for i in range(len(moveset)) if moveset.selected[i]]
        weights = [0] + [moveset.weights[i] for i in range(len(moveset)) if moveset.selected[i]]
        weights[0] = len(move_indices)*10

        return random.choices(move_indices, weights)[0]

    def ai_activate(self) -> bool:
        move_index = self.ai_select_move_index()
        self.current_move = (
            self.attacker.moveset[move_index] if move_index != -1
            else db.move_db.REGULAR_ATTACK
        )
        if success := self.can_activate():
            self.activate(move_index)
        return success

    def can_activate(self) -> bool:
        return (
            self.current_move.activation_condition == "None"
            and target_getter.get_targets(self.attacker, self.dungeon, MoveRange.ALL_ENEMIES_IN_THE_ROOM)
            and self.get_targets()
        )

    def activate(self, move_index: int):
        self.current_move = (
            db.move_db.REGULAR_ATTACK if move_index == -1
            else self.attacker.moveset[move_index] if self.attacker.moveset.can_use(move_index)
            else db.move_db.STRUGGLE
        )
        if self.current_move in self.attacker.moveset:
            self.attacker.moveset.use(move_index)

        self.attacker.has_turn = False

    def deactivate(self):
        self.attacker = None
        self.defender = None
        self.current_move = None
        self.defender_fainted = False
