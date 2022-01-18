from __future__ import annotations
import os
import tile


def get_patterns() -> list[str]:
    pattern_dir = os.path.join(os.getcwd(), "assets", "images", "tilesets", "patterns.txt")
    with open(pattern_dir, "r") as f:
        lines = f.readlines()
    return [line[:-1] for line in lines]


all_patterns = get_patterns()


class Pattern:
    PATTERN_LENGTH = 8

    def __init__(self, terrain: tile.Terrain, surrounding_terrain: list[tile.Terrain]):
        self.set_pattern(terrain, surrounding_terrain)

    def set_pattern(self, terrain, surrounding_terrain):
        self.pattern = [int(t == terrain)
                        for t in surrounding_terrain]

    @classmethod
    def border_pattern(cls) -> Pattern:
        return cls(tile.Terrain.WALL, [tile.Terrain.WALL for _ in range(Pattern.PATTERN_LENGTH)])

    def matches(self, other: str) -> bool:
        WILDCARD = "X"
        for i in range(Pattern.PATTERN_LENGTH):
            if other[i] not in (str(int(self.pattern[i])), WILDCARD):
                return False
        return True

    def get_position(self) -> tuple[int, int]:
        for i, p in enumerate(all_patterns):
            if self.matches(p):
                return (i % 6, i // 6)
