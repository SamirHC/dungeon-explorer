from __future__ import annotations
import os
import tile


def get_patterns() -> list[str]:
    pattern_dir = os.path.join(os.getcwd(), "assets", "tilesets", "patterns.txt")
    with open(pattern_dir, "r") as f:
        lines = f.readlines()
    return [line[:-1] for line in lines]


all_patterns = get_patterns()


class Pattern:
    PATTERN_LENGTH = 8

    def __init__(self, tile_type: tile.Tile, surrounding_tiles: list[tile.Tile]):
        self.set_pattern(tile_type, surrounding_tiles)

    def set_pattern(self, tile_type, surrounding_tiles):
        self.pattern = [int(surrounding_tile == tile_type)
                        for surrounding_tile in surrounding_tiles]

    @classmethod
    def border_pattern(cls) -> Pattern:
        return cls(tile.Tile.WALL, [tile.Tile.WALL for _ in range(cls.PATTERN_LENGTH)])

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
