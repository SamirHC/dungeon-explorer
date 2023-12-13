from pygame import Color

from app.common import text
from app.pokemon.pokemon import Pokemon
from app.move.move import Move


def get_name_color(pokemon: Pokemon) -> Color:
    if pokemon.is_enemy:
        return text.CYAN
    else:
        return pokemon.name_color


def no_pp():
    return (
        text.TextBuilder()
        .set_shadow(True)
        .set_color(text.WHITE)
        .write("You have ran out of PP for this move.")
        .build()
        .render()
    )


def use_move(pokemon: Pokemon, move: Move):
    return (
        text.TextBuilder()
        .set_shadow(True)
        .set_color(get_name_color(pokemon))
        .write(pokemon.data.name)
        .set_color(text.WHITE)
        .write(" used ")
        .set_color(text.LIME)
        .write(move.name)
        .set_color(text.WHITE)
        .write("!")
        .build()
        .render()
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
        .render()
    )


def move_miss(defender: Pokemon):
    return (
        text.TextBuilder()
        .set_shadow(True)
        .set_color(text.WHITE)
        .write("The move missed ")
        .set_color(get_name_color(defender))
        .write(defender.data.name)
        .set_color(text.WHITE)
        .write("!")
        .build()
        .render()
    )


def no_damage(defender: Pokemon):
    return (
        text.TextBuilder()
        .set_shadow(True)
        .set_color(get_name_color(defender))
        .write(defender.data.name)
        .set_color(text.WHITE)
        .write(" took no damage!")
        .build()
        .render()
    )


def calamatous_damage(defender: Pokemon):
    return (
        text.TextBuilder()
        .set_shadow(True)
        .set_color(get_name_color(defender))
        .write(defender.data.name)
        .set_color(text.WHITE)
        .write("took calamitous damage!")
        .build()
        .render()
    )


def damage(defender: Pokemon, amount: int):
    return (
        text.TextBuilder()
        .set_shadow(True)
        .set_color(get_name_color(defender))
        .write(defender.data.name)
        .set_color(text.WHITE)
        .write(" took ")
        .set_color(text.CYAN)
        .write(f"{amount} ")
        .set_color(text.WHITE)
        .write("damage!")
        .build()
        .render()
    )


def defeated(p: Pokemon):
    return (
        text.TextBuilder()
        .set_shadow(True)
        .set_color(get_name_color(p))
        .write(p.data.name)
        .set_color(text.WHITE)
        .write(" was defeated!")
        .build()
        .render()
    )
