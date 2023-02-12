import enum


class Structure(enum.Enum):
    SMALL = "SMALL"
    ONE_ROOM_MH = "ONE_ROOM_MH"
    RING = "RING"
    CROSSROADS = "CROSSROADS"
    TWO_ROOMS_MH = "TWO_ROOMS_MH"
    LINE = "LINE"
    CROSS = "CROSS"
    BEETLE = "BETTLE"
    OUTER_ROOMS = "OUTER_ROOMS"
    MEDIUM = "MEDIUM"
    SMALL_MEDIUM = "SMALL_MEDIUM"
    MEDIUM_LARGE = "MEDIUM_LARGE"
    MEDIUM_LARGE_12 = "MEDIUM_LARGE_12"
    MEDIUM_LARGE_13 = "MEDIUM_LARGE_13"
    MEDIUM_LARGE_14 = "MEDIUM_LARGE_14"
    MEDIUM_LARGE_15 = "MEDIUM_LARGE_15"

    def is_medium_large(self) -> bool:
        return self in (
            Structure.MEDIUM_LARGE,
            Structure.MEDIUM_LARGE_12,
            Structure.MEDIUM_LARGE_13,
            Structure.MEDIUM_LARGE_14,
            Structure.MEDIUM_LARGE_15
        )
