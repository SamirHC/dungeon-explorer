from enum import Enum


class Gender(Enum):
    INVALID = 0
    MALE = 1
    FEMALE = 2
    GENDERLESS = 3

    def get_font_string(self) -> str:
        match self:
            case Gender.MALE:
                return '♂'
            case Gender.FEMALE:
                return '♀'
            case _:
                return ''