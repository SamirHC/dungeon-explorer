from pygame import Color

from app.common import constants
from app.gui import text
from app.pokemon.pokemon import Pokemon
from app.move.move import Move
from app.pokemon.stat import Stat
from app.dungeon.weather import Weather


def get_name_gender_text(pokemon: Pokemon) -> str:
    symbol = pokemon.gender.get_font_string()
    return symbol if pokemon.is_enemy and not pokemon.base.name.endswith(symbol) else ""


def get_name_color(pokemon: Pokemon) -> Color:
    return constants.CYAN if pokemon.is_enemy else pokemon.name_color


def no_pp():
    return text.TextBuilder.build_white("You have ran out of PP for this move.")


def use_move(pokemon: Pokemon, move: Move):
    return (
        text.TextBuilder()
        .set_shadow(True)
        .set_color(get_name_color(pokemon))
        .write(pokemon.base.name)
        .set_color(constants.OFF_WHITE)
        .write(get_name_gender_text(pokemon))
        .write(" used ")
        .set_color(constants.LIME)
        .write(move.name)
        .set_color(constants.OFF_WHITE)
        .write("!")
        .build()
    )


def move_fail():
    return (
        text.TextBuilder()
        .set_shadow(True)
        .set_color(constants.OFF_WHITE)
        .write("The ")
        .set_color(constants.LIME)
        .write("move")
        .set_color(constants.OFF_WHITE)
        .write(" failed!")
        .build()
    )


def move_miss(defender: Pokemon):
    return (
        text.TextBuilder()
        .set_shadow(True)
        .set_color(constants.OFF_WHITE)
        .write("The move missed ")
        .set_color(get_name_color(defender))
        .write(defender.base.name)
        .set_color(constants.OFF_WHITE)
        .write(get_name_gender_text(defender))
        .write("!")
        .build()
    )


def no_damage(defender: Pokemon):
    return (
        text.TextBuilder()
        .set_shadow(True)
        .set_color(get_name_color(defender))
        .write(defender.base.name)
        .set_color(constants.OFF_WHITE)
        .write(get_name_gender_text(defender))
        .write(" took no damage!")
        .build()
    )


def calamatous_damage(defender: Pokemon):
    return (
        text.TextBuilder()
        .set_shadow(True)
        .set_color(get_name_color(defender))
        .write(defender.base.name)
        .set_color(constants.OFF_WHITE)
        .write(get_name_gender_text(defender))
        .write("took calamitous damage!")
        .build()
    )


def damage(defender: Pokemon, amount: int):
    return (
        text.TextBuilder()
        .set_shadow(True)
        .set_color(get_name_color(defender))
        .write(defender.base.name)
        .set_color(constants.OFF_WHITE)
        .write(get_name_gender_text(defender))
        .write(" took ")
        .set_color(constants.CYAN)
        .write(f"{amount} ")
        .set_color(constants.OFF_WHITE)
        .write("damage!")
        .build()
    )


def defeated(p: Pokemon):
    return (
        text.TextBuilder()
        .set_shadow(True)
        .set_color(get_name_color(p))
        .write(p.base.name)
        .set_color(constants.OFF_WHITE)
        .write(get_name_gender_text(p))
        .write(" was defeated!")
        .build()
    )


def gain_xp(p: Pokemon, amount: int):
    return (
        text.TextBuilder()
        .set_shadow(True)
        .set_color(get_name_color(p))
        .write(p.base.name)
        .set_color(constants.OFF_WHITE)
        .write(get_name_gender_text(p))
        .write(" gained ")
        .set_color(constants.CYAN)
        .write(str(amount))
        .set_color(constants.OFF_WHITE)
        .write(" Exp. Points!")
        .build()
    )


def level_up(p: Pokemon, level: int):
    return (
        text.TextBuilder()
        .set_shadow(True)
        .set_color(get_name_color(p))
        .write(p.base.name)
        .set_color(constants.OFF_WHITE)
        .write(get_name_gender_text(p))
        .write(" grew to Level ")
        .set_color(constants.CYAN)
        .write(str(level))
        .set_color(constants.OFF_WHITE)
        .write("!")
        .build()
    )


def hp_up(p: Pokemon, amount: int):
    return (
        text.TextBuilder()
        .set_shadow(True)
        .set_color(get_name_color(p))
        .write(p.base.name)
        .set_color(constants.OFF_WHITE)
        .write(get_name_gender_text(p))
        .write("'s ")
        .set_color(constants.CYAN)
        .write("HP")
        .set_color(constants.OFF_WHITE)
        .write(" went up ")
        .set_color(constants.CYAN)
        .write(str(amount))
        .set_color(constants.OFF_WHITE)
        .write("!")
        .build()
    )


def stat_up(p: Pokemon, stat: Stat, amount: int):
    return (
        text.TextBuilder()
        .set_shadow(True)
        .set_color(get_name_color(p))
        .write(p.base.name)
        .set_color(constants.OFF_WHITE)
        .write(get_name_gender_text(p))
        .write(f"'s {stat.get_log_string()} went up ")
        .set_color(constants.CYAN)
        .write(str(amount))
        .set_color(constants.OFF_WHITE)
        .write("!")
        .build()
    )


def sent_flying(p: Pokemon):
    return (
        text.TextBuilder()
        .set_shadow(True)
        .set_color(get_name_color(p))
        .write(p.base.name)
        .set_color(constants.OFF_WHITE)
        .write(get_name_gender_text(p))
        .write(" was sent flying!")
        .build()
    )


def weather(weather: Weather):
    return text.TextBuilder.build_white(f" Weather: {weather.value.capitalize()}")
