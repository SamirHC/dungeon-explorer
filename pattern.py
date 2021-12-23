import os

def get_patterns() -> list[str]:
        pattern_dir = os.path.join(os.getcwd(), "images", "Tiles.txt")
        with open(pattern_dir, "r") as f:
            lines = f.readlines()
        return [line[:-1] for line in lines]

patterns = get_patterns()

class Pattern:
    PATTERN_LENGTH = 8

    def __init__(self):
        self.pattern = [1 for _ in range(Pattern.PATTERN_LENGTH)]

    def set_pattern(self, direction: int, value: int):
        self.pattern[direction] = value

    def matches(self, other: str):
        WILDCARD = "X"
        for i in range(Pattern.PATTERN_LENGTH):
            if other[i] not in (str(int(self.pattern[i])), WILDCARD):
                return False
        return True

    def get_row_col(self):
        for i in range(len(patterns)):
            if self.matches(patterns[i]):
                return (i // 6, i % 6)
