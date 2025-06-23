import unittest

from app.model.animation import Animation


class TestAnimation(unittest.TestCase):
    def setUp(self):
        self.frames = [1, 2, 3]
        self.durations = [2, 1, 3]
        self.animation = Animation(frames=self.frames, durations=self.durations)

    def _single_iteration(self):
        self.assertEqual(self.animation.get_current_frame(), 1)
        self.animation.update()
        self.assertEqual(self.animation.get_current_frame(), 1)
        self.animation.update()
        self.assertEqual(self.animation.get_current_frame(), 2)
        self.animation.update()
        self.assertEqual(self.animation.get_current_frame(), 3)
        self.animation.update()
        self.assertEqual(self.animation.get_current_frame(), 3)
        self.animation.update()
        self.assertEqual(self.animation.get_current_frame(), 3)
        self.animation.update()

    def test_get_current_frame_initial(self):
        self.assertEqual(self.animation.get_current_frame(), 1)

    def test_get_current_frame_after_update(self):
        self.animation.update()
        self.assertEqual(self.animation.get_current_frame(), 1)

    def test_restart(self):
        for _ in range(3):
            self.animation.update()
        self.animation.restart()
        self.assertEqual(self.animation.get_current_frame(), 1)

    def test_update_single_iteration(self):
        self.animation.iterations = 1
        self._single_iteration()
        self.assertIsNone(self.animation.get_current_frame())

    def test_update_multiple_iterations(self):
        self.animation.iterations = 3
        for _ in range(3):
            self._single_iteration()
        self.assertIsNone(self.animation.get_current_frame())

    def test_update_infinite_iterations(self):
        for _ in range(200):
            self._single_iteration()

    def test_is_restarted_initial(self):
        self.assertTrue(self.animation.is_restarted())

    def test_is_restarted_after_restart(self):
        self.animation.update()
        self.animation.restart()
        self.assertTrue(self.animation.is_restarted())
