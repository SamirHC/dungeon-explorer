from enum import Enum


class Gender(Enum):
    INVALID = 0
    MALE = 1
    FEMALE = 2
    GENDERLESS = 3

    def get_font_string(self) -> list[str]:
        match self:
            case Gender.MALE:
                return [chr(189)]
            case Gender.FEMALE:
                return [chr(190)]
            case _:
                return []