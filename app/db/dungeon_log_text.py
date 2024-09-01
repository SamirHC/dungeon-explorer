from pygame import Color

from app.gui import text
from app.pokemon.pokemon import Pokemon
from app.move.move import Move


def get_name_gender_text(pokemon: Pokemon) -> list[int]:
    return pokemon.gender.get_font_string() if pokemon.is_enemy else []


def get_name_color(pokemon: Pokemon) -> Color:
    return text.CYAN if pokemon.is_enemy else pokemon.name_color


def no_pp():
    return text.TextBuilder.build_white("You have ran out of PP for this move.")


def use_move(pokemon: Pokemon, move: Move):
    return (
        text.TextBuilder()
        .set_shadow(True)
        .set_color(get_name_color(pokemon))
        .write(pokemon.base.name)
        .set_color(text.WHITE)
        .write(get_name_gender_text(pokemon))
        .write(" used ")
        .set_color(text.LIME)
        .write(move.name)
        .set_color(text.WHITE)
        .write("!")
        .build()
    )


def move_fail():
    return (
        text.TextBuilder()
        .set_shadow(True)
        .set_color(text.WHITE)
        .write("The ")
        .set_color(text.LIME)
        .write("move")
        .set_color(text.WHITE)
        .write(" failed!")
        .build()
    )


def move_miss(defender: Pokemon):
    return (
        text.TextBuilder()
        .set_shadow(True)
        .set_color(text.WHITE)
        .write("The move missed ")
        .set_color(get_name_color(defender))
        .write(defender.base.name)
        .set_color(text.WHITE)
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
        .set_color(text.WHITE)
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
        .set_color(text.WHITE)
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
        .set_color(text.WHITE)
        .write(get_name_gender_text(defender))
        .write(" took ")
        .set_color(text.CYAN)
        .write(f"{amount} ")
        .set_color(text.WHITE)
        .write("damage!")
        .build()
    )


def defeated(p: Pokemon):
    return (
        text.TextBuilder()
        .set_shadow(True)
        .set_color(get_name_color(p))
        .write(p.base.name)
        .set_color(text.WHITE)
        .write(get_name_gender_text(p))
        .write(" was defeated!")
        .build()
    )
