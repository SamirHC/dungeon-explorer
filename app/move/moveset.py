from app.move import move


class Moveset:
    MAX_MOVES = 4

    def __init__(self, move_ids: list[int]=None):
        if move_ids is None:
            move_ids = []
        self.moveset: list[move.Move] = []
        for move_id in move_ids:
            m = move.db[move_id]
            self.learn(m)
        self.pp = [m.pp for m in self.moveset]
        self.selected = [True for _ in self.moveset]

    @property
    def weights(self) -> list[int]:
        return [m.weight for m in self]

    def __getitem__(self, index: int) -> move.Move:
        return self.moveset[index]

    def __len__(self) -> int:
        return len(self.moveset)

    def __contains__(self, move: move.Move) -> bool:
        return move in self.moveset

    def can_use(self, index: int):
        return self.pp[index]

    def use(self, index: int):
        self.pp[index] -= 1

    def can_learn(self, move_id: int) -> bool:
        m = move.db[move_id]
        return len(self) != Moveset.MAX_MOVES and m not in self

    def learn(self, move_id: int):
        m = move.db[move_id]
        if self.can_learn(move_id):
            self.moveset.append(m)
            self.pp.append(m.pp)
            self.selected.append(True)

    def forget(self, index: int):
        self.moveset.remove(index)
        self.pp.remove(index)
        self.selected.remove(index)

    def switch(self, index: int):
        self.selected[index] = not self.selected[index]

    def shift_up(self, index: int) -> int:
        if index == 0:
            return index
        self.moveset[index - 1], self.moveset[index] = self[index], self[index - 1]
        self.pp[index - 1], self.pp[index] = self.pp[index], self.pp[index - 1]
        self.selected[index - 1], self.selected[index] = self.selected[index], self.selected[index - 1]
        return index - 1

    def shift_down(self, index: int) -> int:
        if index == len(self) - 1:
            return index
        self.moveset[index], self.moveset[index + 1] = self[index + 1], self[index]
        self.pp[index], self.pp[index + 1] = self.pp[index + 1], self.pp[index]
        self.selected[index], self.selected[index + 1] = self.selected[index + 1], self.selected[index]
        return index + 1
