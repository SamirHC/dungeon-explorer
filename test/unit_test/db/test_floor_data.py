import pytest

from app.dungeon.floor_data import FloorData
from app.db import floor_data


def test_load_for_test_dungeon():
    result = floor_data.load(dungeon_id=0, floor_id=1)
    assert isinstance(result, FloorData)


def test_load_fails_for_invalid_dungeon():
    with pytest.raises(Exception):
        floor_data.load(dungeon_id=29832, floor_id=1)


def test_load_floor_list_for_test_dungeon():
    result = floor_data.load_floor_list(dungeon_id=0)
    assert len(result) == 3
    assert all(isinstance(x, FloorData) for x in result)


if __name__ == "__main__":
    import sys
    pytest.main(sys.argv)
