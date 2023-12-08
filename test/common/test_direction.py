from app.common.direction import Direction

import unittest

class DirectionTest(unittest.TestCase):

    def test_x(self):
        self.assertEqual(0, Direction.NORTH.x)
        self.assertEqual(1, Direction.EAST.x)
        self.assertEqual(-1, Direction.WEST.x)

