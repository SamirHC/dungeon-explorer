import pytest

from app.common import utils


def test_dist_inf_norm():
    p1 = (10, 15)
    p2 = (10, 12)
    p3 = (14, 13)
    
    assert utils.dist_inf_norm(p1, p2) == 3
    assert utils.dist_inf_norm(p1, p3) == 4
    assert utils.dist_inf_norm(p2, p2) == 0


if __name__ == "__main__":
    import sys
    pytest.main(sys.argv)
