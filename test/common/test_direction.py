from app.common.direction import Direction

import unittest


class TestDirection(unittest.TestCase):
    def test_x(self):
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
            self.assertEqual(0, d.x)
        for d in x_is_negative:
            self.assertEqual(-1, d.x)
        for d in x_is_positive:
            self.assertEqual(1, d.x)

    def test_y(self):
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
            self.assertEqual(0, d.y)
        for d in y_is_negative:
            self.assertEqual(-1, d.y)
        for d in y_is_positive:
            self.assertEqual(1, d.y)

    def test_is_horizontal(self):
        vertical_directions = [Direction.EAST, Direction.WEST]
        for d in vertical_directions:
            self.assertTrue(d.is_horizontal())

        other_directions = [
            Direction.NORTH_EAST,
            Direction.NORTH_WEST,
            Direction.NORTH,
            Direction.SOUTH,
            Direction.SOUTH_EAST,
            Direction.SOUTH_WEST,
        ]

        for d in other_directions:
            self.assertFalse(d.is_horizontal())

    def test_is_vertical(self):
        horizontal_directions = [Direction.NORTH, Direction.SOUTH]
        for d in horizontal_directions:
            self.assertTrue(d.is_vertical())

        other_directions = [
            Direction.NORTH_EAST,
            Direction.NORTH_WEST,
            Direction.EAST,
            Direction.WEST,
            Direction.SOUTH_EAST,
            Direction.SOUTH_WEST,
        ]

        for d in other_directions:
            self.assertFalse(d.is_vertical())

    def test_is_diagonal(self):
        diagonal_directions = [
            Direction.SOUTH_WEST,
            Direction.SOUTH_EAST,
            Direction.NORTH_WEST,
            Direction.NORTH_EAST,
        ]
        for d in diagonal_directions:
            self.assertTrue(d.is_diagonal())

        other_directions = [
            Direction.NORTH,
            Direction.SOUTH,
            Direction.EAST,
            Direction.WEST,
        ]
        for d in other_directions:
            self.assertFalse(d.is_diagonal())

    def test_is_cardinal(self):
        cardinal_directions = [
            Direction.NORTH,
            Direction.SOUTH,
            Direction.EAST,
            Direction.WEST,
        ]
        for d in cardinal_directions:
            self.assertTrue(d.is_cardinal())

        other_directions = [
            Direction.SOUTH_WEST,
            Direction.SOUTH_EAST,
            Direction.NORTH_WEST,
            Direction.NORTH_EAST,
        ]
        for d in other_directions:
            self.assertFalse(d.is_cardinal())

    def test_clockwise(self):
        self.assertEqual(Direction.NORTH, Direction.NORTH_WEST.clockwise())
        self.assertEqual(Direction.NORTH_EAST, Direction.NORTH.clockwise())
        self.assertEqual(Direction.EAST, Direction.NORTH_EAST.clockwise())
        self.assertEqual(Direction.SOUTH_EAST, Direction.EAST.clockwise())
        self.assertEqual(Direction.SOUTH, Direction.SOUTH_EAST.clockwise())
        self.assertEqual(Direction.SOUTH_WEST, Direction.SOUTH.clockwise())
        self.assertEqual(Direction.WEST, Direction.SOUTH_WEST.clockwise())
        self.assertEqual(Direction.NORTH_WEST, Direction.WEST.clockwise())

    def test_anticlockwise(self):
        self.assertEqual(Direction.NORTH, Direction.NORTH_EAST.anticlockwise())
        self.assertEqual(Direction.NORTH_EAST, Direction.EAST.anticlockwise())
        self.assertEqual(Direction.EAST, Direction.SOUTH_EAST.anticlockwise())
        self.assertEqual(Direction.SOUTH_EAST, Direction.SOUTH.anticlockwise())
        self.assertEqual(Direction.SOUTH, Direction.SOUTH_WEST.anticlockwise())
        self.assertEqual(Direction.SOUTH_WEST, Direction.WEST.anticlockwise())
        self.assertEqual(Direction.WEST, Direction.NORTH_WEST.anticlockwise())
        self.assertEqual(Direction.NORTH_WEST, Direction.NORTH.anticlockwise())

    def test_clockwise90(self):
        self.assertEqual(Direction.NORTH, Direction.WEST.clockwise90())
        self.assertEqual(Direction.NORTH_EAST, Direction.NORTH_WEST.clockwise90())
        self.assertEqual(Direction.EAST, Direction.NORTH.clockwise90())
        self.assertEqual(Direction.SOUTH_EAST, Direction.NORTH_EAST.clockwise90())
        self.assertEqual(Direction.SOUTH, Direction.EAST.clockwise90())
        self.assertEqual(Direction.SOUTH_WEST, Direction.SOUTH_EAST.clockwise90())
        self.assertEqual(Direction.WEST, Direction.SOUTH.clockwise90())
        self.assertEqual(Direction.NORTH_WEST, Direction.SOUTH_WEST.clockwise90())

    def test_anticlockwise90(self):
        self.assertEqual(Direction.NORTH, Direction.EAST.anticlockwise90())
        self.assertEqual(Direction.NORTH_EAST, Direction.SOUTH_EAST.anticlockwise90())
        self.assertEqual(Direction.EAST, Direction.SOUTH.anticlockwise90())
        self.assertEqual(Direction.SOUTH_EAST, Direction.SOUTH_WEST.anticlockwise90())
        self.assertEqual(Direction.SOUTH, Direction.WEST.anticlockwise90())
        self.assertEqual(Direction.SOUTH_WEST, Direction.NORTH_WEST.anticlockwise90())
        self.assertEqual(Direction.WEST, Direction.NORTH.anticlockwise90())
        self.assertEqual(Direction.NORTH_WEST, Direction.NORTH_EAST.anticlockwise90())

    def test_flip(self):
        self.assertEqual(Direction.NORTH, Direction.SOUTH.flip())
        self.assertEqual(Direction.NORTH_EAST, Direction.SOUTH_WEST.flip())
        self.assertEqual(Direction.EAST, Direction.WEST.flip())
        self.assertEqual(Direction.SOUTH_EAST, Direction.NORTH_WEST.flip())
        self.assertEqual(Direction.SOUTH, Direction.NORTH.flip())
        self.assertEqual(Direction.SOUTH_WEST, Direction.NORTH_EAST.flip())
        self.assertEqual(Direction.WEST, Direction.EAST.flip())
        self.assertEqual(Direction.NORTH_WEST, Direction.SOUTH_EAST.flip())
