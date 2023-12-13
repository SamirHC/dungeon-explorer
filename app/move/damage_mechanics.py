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


STAB = 1.5  # Same Type Attack Bonus
CRITICAL = 1.5


# Algorithm for Determining Damage
def _get_a_d(attacker: Pokemon, defender: Pokemon, category: MoveCategory):
    atk_stat = Stat.ATTACK if category is MoveCategory.PHYSICAL else Stat.SP_ATTACK
    def_stat = Stat.DEFENSE if category is MoveCategory.PHYSICAL else Stat.SP_DEFENSE
    a = attacker.stats.attack.value
    a_stage = attacker.status.stat_stages[atk_stat].value
    d = defender.stats.defense.value
    d_stage = defender.status.stat_stages[def_stat].value

    A = a * db.stat_stage_chart.get_attack_multiplier(a_stage)
    D = d * db.stat_stage_chart.get_defense_multiplier(d_stage)
    return A, D


def _calculate_raw_damage(
    dungeon: Dungeon, attacker: Pokemon, defender: Pokemon, move: Move
):
    A, D = _get_a_d(attacker, defender, move.category)
    L = attacker.stats.level.value
    P = move.power
    Y = 1 if defender in dungeon.party else 340 / 256

    return (
        (A + P) * (39168 / 65536)
        - (D / 2)
        + 50 * utils.clamp(1, math.log(((A - D) / 8 + L + 50) * 10), 4095)
        - 311
    ) / Y


def _weather_multiplier(weather: Weather, move_type: Type):
    if weather is Weather.CLOUDY and move_type is not Type.NORMAL:
        return 0.75

    multipliers = {
        (Weather.FOG, Type.ELECTRIC): 0.5,
        (Weather.RAINY, Type.FIRE): 0.5,
        (Weather.RAINY, Type.WATER): 1.5,
        (Weather.SUNNY, Type.WATER): 0.5,
        (Weather.SUNNY, Type.FIRE): 1.5,
    }

    return multipliers.get((weather, move_type), 1)


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
    # TODO: Step 1 - Stat Modifications
    # Step 2 - Raw Damage Calculation
    damage = _calculate_raw_damage(dungeon, attacker, defender, move)
    # Step 3 - Final Damage Modifications
    damage = utils.clamp(1, damage, 999)

    multiplier = 1
    multiplier *= db.type_chart.get_move_effectiveness(move.type, defender.data.type).value
    multiplier *= STAB if move.type in attacker.data.type else 1
    multiplier *= _weather_multiplier(dungeon.floor.status.weather, move.type)
    multiplier *= (
        CRITICAL if calculate_critical(dungeon, attacker, defender, move) else 1
    )

    # Step 4 - Final Calculations
    damage *= multiplier
    # TODO: Change optional_multiplier to use data from Move flags
    damage *= optional_multiplier
    damage *= (random.randint(0, 16383) + 57344) / 65536
    damage = round(damage)

    return damage


# Algorithm for Accuracy
def calculate_accuracy(
    dungeon: Dungeon, attacker: Pokemon, defender: Pokemon, move: Move
) -> bool:
    D, E, F = 0, 0, 0
    # Snatch
    # Lightning-Rod
    # Passing Moves
    # Magic Coat
    # Mirror Move
    # Protect

    # Flying, Bouncing, Diving and Digging
    if defender.has_status_effect(StatusEffect.DIGGING):
        # TODO: Earthquake, Magnitude hits
        return False
    # Soundproof

    if E == 1 and move.name in ("Protect", "Detect", "Endure"):
        F = 1
    if F == 1 and attacker is defender:
        return True
    # Sure-Hit Attacker
    # Sure Shot
    # Whiffer

    if move.accuracy <= 100:
        # Detect Band
        # Quick Dodger
        # Compoundeyes
        if move.name == "Thunder" and dungeon.floor.status.weather is Weather.RAINY:
            return True
        if move.name == "Thunder" and dungeon.floor.status.weather is Weather.SUNNY:
            acc_stage -= 2

        acc_stage = utils.clamp(0, acc_stage, 20)
        acc = move.accuracy * db.stat_stage_chart.get_accuracy_multiplier(acc_stage)

        eva_stage = defender.status.stat_stages[Stat.EVASION].value
        # Sand Veil during Sandstorm
        # Hustle
        eva_stage = utils.clamp(0, eva_stage, 20)
        acc *= db.stat_stage_chart.get_evasion_multiplier(eva_stage)

        return utils.is_success(acc)

    return True


# Algorithm for Critical Hits
def calculate_critical(
    dungeon: Dungeon, attacker: Pokemon, defender: Pokemon, move: Move
) -> bool:
    # Sequence exits
    if move.category is MoveCategory.OTHER:
        return False

    C = move.critical
    # Gender
    if attacker.has_status_effect(StatusEffect.FOCUS_ENERGY):
        C = 999
    # Scope Lens, Patsy Band
    # Type-Advantage Master
    return utils.is_success(C)
