import math
import random

from app.common import utils
import app.db.database as db
from app.move.move import MoveCategory, Move, Type
from app.pokemon.pokemon import Pokemon
from app.pokemon.stat import Stat
from app.pokemon.status_effect import StatusEffect
from app.dungeon.weather import Weather
from app.dungeon.dungeon import Dungeon


"""
This is based on the article "Damage Mechanics Guide (DS)" by Eevee-Trainer / 
_Cecilia_. 

The article can be found at:
https://gamefaqs.gamespot.com/ds/938931-pokemon-mystery-dungeon-explorers-of-time/faqs/75112/damage-mechanics-guide#algorithm-for-determining-damage
"""


def calculate_damage(
    dungeon: Dungeon,
    attacker: Pokemon,
    defender: Pokemon,
    move: Move,
    optional_multiplier=1,
) -> int:
    # Step 0 - Special Exceptions
    if move.category is MoveCategory.OTHER:
        return 0
    if attacker.status.belly.value == 0 and attacker is not dungeon.party.leader:
        return 1
    # Step 1 - Stat Modifications
    # Step 2 - Raw Damage Calculation
    if move.category is MoveCategory.PHYSICAL:
        a = attacker.attack
        a_stage = attacker.status.stat_stages[Stat.ATTACK].value
        d = defender.defense
        d_stage = defender.status.stat_stages[Stat.DEFENSE].value
    elif move.category is MoveCategory.SPECIAL:
        a = attacker.attack
        a_stage = attacker.status.stat_stages[Stat.ATTACK].value
        d = defender.defense
        d_stage = defender.status.stat_stages[Stat.DEFENSE].value

    A = a * db.stat_stage_chart.get_attack_multiplier(a_stage)
    D = d * db.stat_stage_chart.get_defense_multiplier(d_stage)
    L = attacker.level
    P = move.power
    if defender not in dungeon.party:
        Y = 340 / 256
    else:
        Y = 1

    damage = (
        (A + P) * (39168 / 65536)
        - (D / 2)
        + 50 * math.log(((A - D) / 8 + L + 50) * 10)
        - 311
    ) / Y

    # Step 3 - Final Damage Modifications
    if damage < 1:
        damage = 1
    elif damage > 999:
        damage = 999

    multiplier = 1
    multiplier *= db.type_chart.get_move_effectiveness(move.type, defender.type).value

    # STAB bonus
    if move.type in attacker.type:
        multiplier *= 1.5

    if dungeon.floor.status.weather is Weather.CLOUDY:
        if move.type is not Type.NORMAL:
            multiplier *= 0.75
    elif dungeon.floor.status.weather is Weather.FOG:
        if move.type is Type.ELECTRIC:
            multiplier *= 0.5
    elif dungeon.floor.status.weather is Weather.RAINY:
        if move.type is Type.FIRE:
            multiplier *= 0.5
        elif move.type is Type.WATER:
            multiplier *= 1.5
    elif dungeon.floor.status.weather is Weather.SUNNY:
        if move.type is Type.WATER:
            multiplier *= 0.5
        elif move.type is Type.FIRE:
            multiplier *= 1.5

    if utils.is_success(move.critical):
        multiplier *= 1.5

    # Step 4 - Final Calculations
    damage *= multiplier
    damage *= optional_multiplier
    damage *= (random.randint(0, 16383) + 57344) / 65536
    damage = round(damage)

    return damage


def miss(dungeon: Dungeon, attacker: Pokemon, defender: Pokemon, move: Move) -> bool:
    if defender.has_status_effect(StatusEffect.DIGGING):
        return True

    move_acc = move.accuracy
    if move_acc > 100:
        return False

    acc_stage = attacker.status.stat_stages[Stat.ACCURACY].value
    if move.name == "Thunder":
        if dungeon.floor.status.weather is Weather.RAINY:
            return False
        elif dungeon.floor.status.weather is Weather.SUNNY:
            acc_stage -= 2
    if acc_stage < 0:
        acc_stage = 0
    elif acc_stage > 20:
        acc_stage = 20
    acc = move_acc * db.stat_stage_chart.get_accuracy_multiplier(acc_stage)

    eva_stage = defender.status.stat_stages[Stat.EVASION].value
    if eva_stage < 0:
        eva_stage = 0
    elif eva_stage > 20:
        eva_stage = 20
    acc *= db.stat_stage_chart.get_evasion_multiplier(eva_stage)

    return not utils.is_success(acc)
