from dungeon_explorer.move import move


class Moveset:
    MAX_MOVES = 4

    def __init__(self, moveset: list[move.Move]=None):
        if moveset is None:
            moveset = []
        self.moveset: list[move.Move] = []
        for m in moveset:
            self.learn(m)
        self.pp = [m.pp for m in self.moveset]

    def __getitem__(self, index: int) -> move.Move:
        return self.moveset[index]

    def __len__(self) -> int:
        return len(self.moveset)

    def __contains__(self, move: move.Move) -> bool:
        return move.name in [m.name for m in self.moveset]

    def can_use(self, index: int):
        return self.pp[index]

    def use(self, index: int):
        self.pp[index] -= 1

    def can_learn(self, move: move.Move) -> bool:
        return len(self) != Moveset.MAX_MOVES and move not in self

    def learn(self, move: move.Move):
        if self.can_learn(move):
            self.moveset.append(move)
            self.pp.append(move.pp)

    def forget(self, index: int):
        self.moveset.remove(index)
        self.pp.remove(index)

    def shift_up(self, index: int) -> int:
        if index == 0:
            return index
        self.moveset[index - 1], self.moveset[index] = self[index], self[index - 1]
        self.pp[index - 1], self.pp[index] = self.pp[index], self.pp[index - 1]
        return index - 1

    def shift_down(self, index: int) -> int:
        if index == len(self) - 1:
            return index
        self.moveset[index], self.moveset[index + 1] = self[index + 1], self[index]
        self.pp[index], self.pp[index + 1] = self.pp[index + 1], self.pp[index]
        return index + 1

    def get_weights(self) -> list[int]:
        return [m.weight for m in self]