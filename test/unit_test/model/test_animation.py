import pytest

from app.model.animation import Animation


@pytest.fixture(scope="function")
def animation() -> Animation:
    return Animation(frames=[1, 2, 3], durations=[2, 1, 3])

def _single_iteration(animation: Animation):
    assert animation.get_current_frame() == 1
    animation.update()
    assert animation.get_current_frame() == 1
    animation.update()
    assert animation.get_current_frame() == 2
    animation.update()
    assert animation.get_current_frame() == 3
    animation.update()
    assert animation.get_current_frame() == 3
    animation.update()
    assert animation.get_current_frame() == 3
    animation.update()

def test_get_current_frame_initial(animation: Animation):
    assert animation.get_current_frame() == 1

def test_get_current_frame_after_update(animation: Animation):
    animation.update()
    assert animation.get_current_frame() == 1

def test_restart(animation: Animation):
    for _ in range(3):
        animation.update()
    animation.restart()
    assert animation.get_current_frame() == 1

def test_update_single_iteration(animation: Animation):
    animation.iterations = 1
    _single_iteration(animation)
    assert animation.get_current_frame() is None

def test_update_multiple_iterations(animation: Animation):
    animation.iterations = 3
    for _ in range(3):
        _single_iteration(animation)
    assert animation.get_current_frame() is None

def test_update_infinite_iterations(animation: Animation):
    for _ in range(200):
        _single_iteration(animation)

def test_is_restarted_initial(animation: Animation):
    assert animation.is_restarted()

def test_is_restarted_after_restart(animation: Animation):
    animation.update()
    animation.restart()
    assert animation.is_restarted()


if __name__ == "__main__":
    import sys
    pytest.main(sys.argv)
