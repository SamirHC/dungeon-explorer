import unittest

from app.common import utils


class TestUtils(unittest.TestCase):
    def test_dist_inf_norm(self):
        p1 = (10, 15)
        p2 = (10, 12)
        p3 = (14, 13)
        
        self.assertEqual(utils.dist_inf_norm(p1, p2), 3)
        self.assertEqual(utils.dist_inf_norm(p1, p3), 4)
        self.assertEqual(utils.dist_inf_norm(p2, p2), 0)
