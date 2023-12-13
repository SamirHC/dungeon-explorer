import unittest
from app.model.bounded_int import BoundedInt


class TestBoundedInt(unittest.TestCase):
    def setUp(self):
        self.b = BoundedInt(value=5, min_value=0, max_value=10)

    def test_set_value_within_bounds(self):
        self.b.set(7)
        self.assertEqual(self.b.value, 7)

    def test_set_value_below_min(self):
        self.b.set(-2)
        self.assertEqual(self.b.value, 0)

    def test_set_value_above_max(self):
        self.b.set(15)
        self.assertEqual(self.b.value, 10)

    def test_add_positive(self):
        self.b.add(3)
        self.assertEqual(self.b.value, 8)
    
    def test_add_negative(self):
        self.b.add(-3)
        self.assertEqual(self.b.value, 2)
    
    def test_add_above_max(self):
        self.b.add(100)
        self.assertEqual(self.b.value, 10)
    
    def test_add_below_min(self):
        self.b.add(-100)
        self.assertEqual(self.b.value, 0)

    def test_eq(self):
        b1 = BoundedInt(value=5, min_value=0, max_value=10)
        b2 = BoundedInt(value=5, min_value=0, max_value=10)
        self.assertEqual(b1, b2)

    def test_not_eq(self):
        b1 = BoundedInt(value=5, min_value=0, max_value=10)
        b2 = BoundedInt(value=7, min_value=0, max_value=10)
        self.assertNotEqual(b1, b2)

    def test_str(self):
        self.assertEqual(str(self.b), "5")

    def test_repr(self):
        self.assertEqual(repr(self.b), "0 <= 5 <= 10")
