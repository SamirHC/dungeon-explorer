import pytest

from app.model.moving_entity import MovingEntity


@pytest.fixture(scope="function")
def entity() -> MovingEntity:
    return MovingEntity()

def test_initial_position(entity: MovingEntity):
    assert entity.position == (0, 0)

def test_start_and_update_movement(entity: MovingEntity):
    T = 5
    entity.start(dest_x=5, dest_y=5, time=T)

    for _ in range(T):
        entity.update()

    assert entity.position == (5, 5)

def test_partial_movement(entity: MovingEntity):
    entity.start(dest_x=10, dest_y=10, time=5)

    for _ in range(3):
        entity.update()

    assert entity.position == pytest.approx((6, 6))

def test_update_without_movement(entity: MovingEntity):
    entity.update()

    assert entity.position == (0, 0)

def test_repeated_start_and_update_movement(entity: MovingEntity):
    entity.start(dest_x=5, dest_y=5, time=5)
    for _ in range(5):
        entity.update()
    assert entity.position == (5, 5)

    entity.start(dest_x=10, dest_y=5, time=2)
    for _ in range(2):
        entity.update()
    assert entity.position == (10, 5)

    entity.start(dest_x=0, dest_y=0, time=20)
    for _ in range(20):
        entity.update()
    assert entity.position == (0, 0)

def test_repeated_partial_movement(entity: MovingEntity):
    entity.start(dest_x=10, dest_y=10, time=5)
    for _ in range(3):
        entity.update()
    assert entity.position == pytest.approx((6, 6))

    for _ in range(2):
        entity.update()
    assert entity.position == (10, 10)

    entity.start(dest_x=30, dest_y=10, time=10)
    for _ in range(7):
        entity.update()
    assert entity.position == pytest.approx((24, 10))

def test_not_moving_after_time_exceeded(entity: MovingEntity):
    entity.start(dest_x=10, dest_y=10, time=5)
    for _ in range(5):
        assert entity.is_moving
        entity.update()
    assert not entity.is_moving


if __name__ == "__main__":
    import sys
    pytest.main(sys.argv)
