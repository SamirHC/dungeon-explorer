import pytest

from app.model.bounded_int import BoundedInt


@pytest.fixture(scope="function")
def b():
    return BoundedInt(value=5, min_value=0, max_value=10)

def test_set_value_within_bounds(b: BoundedInt):
    b.set(7)
    assert b.value == 7

def test_set_value_below_min(b: BoundedInt):
    b.set(-2)
    assert b.value == 0

def test_set_value_above_max(b: BoundedInt):
    b.set(15)
    assert b.value == 10

def test_add_positive(b: BoundedInt):
    b.add(3)
    assert b.value == 8

def test_add_negative(b: BoundedInt):
    b.add(-3)
    assert b.value == 2

def test_add_above_max(b: BoundedInt):
    b.add(100)
    assert b.value == 10

def test_add_below_min(b: BoundedInt):
    b.add(-100)
    assert b.value == 0

def test_eq():
    b1 = BoundedInt(value=5, min_value=0, max_value=10)
    b2 = BoundedInt(value=5, min_value=0, max_value=10)
    assert b1 == b2

def test_not_eq():
    b1 = BoundedInt(value=5, min_value=0, max_value=10)
    b2 = BoundedInt(value=7, min_value=0, max_value=10)
    assert b1 != b2

def test_str(b: BoundedInt):
    assert str(b) == "5"

def test_repr(b: BoundedInt):
    assert repr(b) == "0 <= 5 <= 10"


if __name__ == "__main__":
    import sys
    pytest.main(sys.argv)
