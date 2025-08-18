import pytest

from app.pokemon.level_up_moves import LevelUpMoves


def test_returns_moves_below_or_equal_level():
    moves = LevelUpMoves(levels=(1, 5, 10), move_ids=(101, 143, 123))
    assert moves.moves_for_level(6) == (101, 143)


def test_returns_empty_if_no_moves():
    moves = LevelUpMoves(levels=(5, 10), move_ids=(101, 102))
    assert moves.moves_for_level(1) == tuple()


def test_returns_all_if_level_high_enough():
    moves = LevelUpMoves(levels=(1, 5), move_ids=(101, 102))
    assert moves.moves_for_level(10) == (101, 102)


def test_handles_duplicate_levels():
    moves = LevelUpMoves(levels=(5, 5, 10), move_ids=(101, 102, 103))
    assert moves.moves_for_level(5) == (101, 102)


def test_requires_preserves_order():
    with pytest.raises(ValueError):
        LevelUpMoves(levels=(3, 1, 2), move_ids=(101, 102, 103))


def test_requires_equal_length_inputs():
    with pytest.raises(ValueError):
        LevelUpMoves(levels=(1, 2, 4, 7), move_ids=(101, 102, 103))
    
    with pytest.raises(ValueError):
        LevelUpMoves(levels=(1, 2, 4, 7), move_ids=(101, 102, 103, 192, 289))


if __name__ == "__main__":
    import sys
    pytest.main(sys.argv)
