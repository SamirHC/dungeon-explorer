from enum import Enum, auto


class Stat(Enum):
    ATTACK = auto()
    DEFENSE = auto()
    SP_ATTACK = auto()
    SP_DEFENSE = auto()
    EVASION = auto()
    ACCURACY = auto()

    def get_log_string(self) -> str:
        match self:
            case Stat.ATTACK:
                return "Attack"
            case Stat.DEFENSE:
                return "Defense"
            case Stat.SP_ATTACK:
                return "Sp. Atk."
            case Stat.SP_DEFENSE:
                return "Sp. Def."
            case Stat.EVASION:
                return "evasion"
            case Stat.ACCURACY:
                return "accuracy"
