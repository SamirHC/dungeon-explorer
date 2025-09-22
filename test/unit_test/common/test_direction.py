import pytest

from app.common.direction import Direction


def test_x():
    x_is_zero = [Direction.NORTH, Direction.SOUTH]
    x_is_positive = [
        Direction.NORTH_EAST,
        Direction.EAST,
        Direction.SOUTH_EAST,
    ]
    x_is_negative = [
        Direction.NORTH_WEST,
        Direction.WEST,
        Direction.SOUTH_WEST,
    ]

    for d in x_is_zero:
        assert 0 == d.x
    for d in x_is_negative:
        assert -1 == d.x
    for d in x_is_positive:
        assert 1 == d.x

def test_y():
    y_is_zero = [Direction.EAST, Direction.WEST]
    y_is_positive = [
        Direction.SOUTH_EAST,
        Direction.SOUTH,
        Direction.SOUTH_WEST,
    ]
    y_is_negative = [
        Direction.NORTH_EAST,
        Direction.NORTH,
        Direction.NORTH_WEST,
    ]

    for d in y_is_zero:
        assert 0 == d.y
    for d in y_is_negative:
        assert -1 == d.y
    for d in y_is_positive:
        assert 1 == d.y

def test_is_horizontal():
    vertical_directions = [Direction.EAST, Direction.WEST]
    for d in vertical_directions:
        assert d.is_horizontal()

    other_directions = [
        Direction.NORTH_EAST,
        Direction.NORTH_WEST,
        Direction.NORTH,
        Direction.SOUTH,
        Direction.SOUTH_EAST,
        Direction.SOUTH_WEST,
    ]

    for d in other_directions:
        assert not d.is_horizontal()

def test_is_vertical():
    horizontal_directions = [Direction.NORTH, Direction.SOUTH]
    for d in horizontal_directions:
        assert d.is_vertical()

    other_directions = [
        Direction.NORTH_EAST,
        Direction.NORTH_WEST,
        Direction.EAST,
        Direction.WEST,
        Direction.SOUTH_EAST,
        Direction.SOUTH_WEST,
    ]

    for d in other_directions:
        assert not d.is_vertical()

def test_is_diagonal():
    diagonal_directions = [
        Direction.SOUTH_WEST,
        Direction.SOUTH_EAST,
        Direction.NORTH_WEST,
        Direction.NORTH_EAST,
    ]
    for d in diagonal_directions:
        assert d.is_diagonal()

    other_directions = [
        Direction.NORTH,
        Direction.SOUTH,
        Direction.EAST,
        Direction.WEST,
    ]
    for d in other_directions:
        assert not d.is_diagonal()

def test_is_cardinal():
    cardinal_directions = [
        Direction.NORTH,
        Direction.SOUTH,
        Direction.EAST,
        Direction.WEST,
    ]
    for d in cardinal_directions:
        assert d.is_cardinal()

    other_directions = [
        Direction.SOUTH_WEST,
        Direction.SOUTH_EAST,
        Direction.NORTH_WEST,
        Direction.NORTH_EAST,
    ]
    for d in other_directions:
        assert not d.is_cardinal()

def test_clockwise():
    assert Direction.NORTH is Direction.NORTH_WEST.clockwise()
    assert Direction.NORTH_EAST is Direction.NORTH.clockwise()
    assert Direction.EAST is Direction.NORTH_EAST.clockwise()
    assert Direction.SOUTH_EAST is Direction.EAST.clockwise()
    assert Direction.SOUTH is Direction.SOUTH_EAST.clockwise()
    assert Direction.SOUTH_WEST is Direction.SOUTH.clockwise()
    assert Direction.WEST is Direction.SOUTH_WEST.clockwise()
    assert Direction.NORTH_WEST is Direction.WEST.clockwise()

def test_anticlockwise():
    assert Direction.NORTH is Direction.NORTH_EAST.anticlockwise()
    assert Direction.NORTH_EAST is Direction.EAST.anticlockwise()
    assert Direction.EAST is Direction.SOUTH_EAST.anticlockwise()
    assert Direction.SOUTH_EAST is Direction.SOUTH.anticlockwise()
    assert Direction.SOUTH is Direction.SOUTH_WEST.anticlockwise()
    assert Direction.SOUTH_WEST is Direction.WEST.anticlockwise()
    assert Direction.WEST is Direction.NORTH_WEST.anticlockwise()
    assert Direction.NORTH_WEST is Direction.NORTH.anticlockwise()

def test_clockwise90():
    assert Direction.NORTH is Direction.WEST.clockwise90()
    assert Direction.NORTH_EAST is Direction.NORTH_WEST.clockwise90()
    assert Direction.EAST is Direction.NORTH.clockwise90()
    assert Direction.SOUTH_EAST is Direction.NORTH_EAST.clockwise90()
    assert Direction.SOUTH is Direction.EAST.clockwise90()
    assert Direction.SOUTH_WEST is Direction.SOUTH_EAST.clockwise90()
    assert Direction.WEST is Direction.SOUTH.clockwise90()
    assert Direction.NORTH_WEST is Direction.SOUTH_WEST.clockwise90()

def test_anticlockwise90():
    assert Direction.NORTH is Direction.EAST.anticlockwise90()
    assert Direction.NORTH_EAST is Direction.SOUTH_EAST.anticlockwise90()
    assert Direction.EAST is Direction.SOUTH.anticlockwise90()
    assert Direction.SOUTH_EAST is Direction.SOUTH_WEST.anticlockwise90()
    assert Direction.SOUTH is Direction.WEST.anticlockwise90()
    assert Direction.SOUTH_WEST is Direction.NORTH_WEST.anticlockwise90()
    assert Direction.WEST is Direction.NORTH.anticlockwise90()
    assert Direction.NORTH_WEST is Direction.NORTH_EAST.anticlockwise90()

def test_flip():
    assert Direction.NORTH is Direction.SOUTH.flip()
    assert Direction.NORTH_EAST is Direction.SOUTH_WEST.flip()
    assert Direction.EAST is Direction.WEST.flip()
    assert Direction.SOUTH_EAST is Direction.NORTH_WEST.flip()
    assert Direction.SOUTH is Direction.NORTH.flip()
    assert Direction.SOUTH_WEST is Direction.NORTH_EAST.flip()
    assert Direction.WEST is Direction.EAST.flip()
    assert Direction.NORTH_WEST is Direction.SOUTH_EAST.flip()


if __name__ == '__main__':
    import sys
    pytest.main(sys.argv)
