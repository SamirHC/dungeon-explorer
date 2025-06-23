import unittest

from app.model.moving_entity import MovingEntity


class TestMovingEntity(unittest.TestCase):
    def setUp(self):
        self.entity = MovingEntity()

    def test_initial_position(self):
        self.assertEqual(self.entity.position, (0, 0))

    def test_start_and_update_movement(self):
        T = 5
        self.entity.start(dest_x=5, dest_y=5, time=T)

        for _ in range(T):
            self.entity.update()

        self.assertEqual(self.entity.position, (5, 5))

    def test_partial_movement(self):
        self.entity.start(dest_x=10, dest_y=10, time=5)

        for _ in range(3):
            self.entity.update()

        self.assertAlmostEqual(self.entity.position, (6, 6), delta=0.01)

    def test_update_without_movement(self):
        self.entity.update()

        self.assertEqual(self.entity.position, (0, 0))

    def test_repeated_start_and_update_movement(self):
        self.entity.start(dest_x=5, dest_y=5, time=5)
        for _ in range(5):
            self.entity.update()
        self.assertEqual(self.entity.position, (5, 5))

        self.entity.start(dest_x=10, dest_y=5, time=2)
        for _ in range(2):
            self.entity.update()
        self.assertEqual(self.entity.position, (10, 5))

        self.entity.start(dest_x=0, dest_y=0, time=20)
        for _ in range(20):
            self.entity.update()
        self.assertEqual(self.entity.position, (0, 0))

    def test_repeated_partial_movement(self):
        self.entity.start(dest_x=10, dest_y=10, time=5)
        for _ in range(3):
            self.entity.update()
        self.assertAlmostEqual(self.entity.position, (6, 6), delta=0.01)

        for _ in range(2):
            self.entity.update()
        self.assertEqual(self.entity.position, (10, 10))

        self.entity.start(dest_x=30, dest_y=10, time=10)
        for _ in range(7):
            self.entity.update()
        self.assertAlmostEqual(self.entity.position, (24, 10), delta=0.01)

    def test_not_moving_after_time_exceeded(self):
        self.entity.start(dest_x=10, dest_y=10, time=5)
        for _ in range(5):
            self.assertTrue(self.entity.is_moving)
            self.entity.update()
        self.assertFalse(self.entity.is_moving)
