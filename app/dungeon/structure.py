from enum import Enum


class Structure(Enum):
    """
    This enum represents each floor structure that can be generated in the
    pseudorandomly generated dungeons. These are pre-determined for each floor
    for each dungeon and is extracted from the database with the string
    representation.
    """

    SMALL = "SMALL"
    ONE_ROOM_MH = "ONE_ROOM_MH"
    RING = "RING"
    CROSSROADS = "CROSSROADS"
    TWO_ROOMS_MH = "TWO_ROOMS_MH"
    LINE = "LINE"
    CROSS = "CROSS"
    BEETLE = "BETTLE"  # Typo is necessary (typo present in XML files)
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
            Structure.MEDIUM_LARGE_15,
        )
