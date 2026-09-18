import string

import pytest

from py_simple_package.src.py_simple import (
    pick_random_items as public_pick_random_items,
    random_float as public_random_float,
)
from py_simple_package.src.py_simple.easy_random import (
    flip_coin,
    generate_simple_password,
    pick_random_item,
    pick_random_items,
    random_bool,
    random_float,
    random_int,
    roll_dice,
    shuffle_list,
)


def test_roll_dice():
    for _ in range(50):
        res = roll_dice(6)
        assert 1 <= res <= 6

    with pytest.raises(ValueError):
        roll_dice(0)


def test_flip_coin():
    outcomes = {flip_coin() for _ in range(50)}
    assert outcomes.issubset({"Heads", "Tails"})


def test_pick_random_item():
    items = ["apple", "banana", "cherry"]
    for _ in range(20):
        assert pick_random_item(items) in items

    with pytest.raises(ValueError):
        pick_random_item([])


def test_pick_random_items(monkeypatch):
    items = ["Ada", "Lin", "Sam"]
    received = {}

    def fake_sample(population, k):
        received.update(population=population, count=k)
        return list(population)[:k]

    monkeypatch.setattr("py_simple.easy_random.random.sample", fake_sample)

    assert pick_random_items(items, 2) == ["Ada", "Lin"]
    assert received == {"population": items, "count": 2}
    assert items == ["Ada", "Lin", "Sam"]
    assert pick_random_items(items, 0) == []


@pytest.mark.parametrize("count", [-1, 4, 1.5, True])
def test_pick_random_items_rejects_invalid_count(count):
    with pytest.raises(ValueError, match="count must be"):
        pick_random_items(["Ada", "Lin", "Sam"], count)


def test_pick_random_items_is_available_from_public_api():
    assert public_pick_random_items is pick_random_items


def test_shuffle_list():
    original = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    shuffled = shuffle_list(original)
    assert len(shuffled) == len(original)
    assert set(shuffled) == set(original)
    assert original == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    assert shuffle_list([]) == []


def test_random_int():
    for _ in range(50):
        val = random_int(5, 15)
        assert 5 <= val <= 15

    with pytest.raises(ValueError):
        random_int(10, 5)


def test_random_bool(monkeypatch):
    assert isinstance(random_bool(), bool)

    monkeypatch.setattr(
        "py_simple_package.src.py_simple.easy_random.random.choice",
        lambda seq: True,
    )
    assert random_bool() is True

    monkeypatch.setattr(
        "py_simple_package.src.py_simple.easy_random.random.choice",
        lambda seq: False,
    )
    assert random_bool() is False

def test_roll_dice_default_sides():
    for _ in range(40):
        result = roll_dice()
        assert 1 <= result <= 6


def test_roll_dice_custom_sides():
    for _ in range(40):
        result = roll_dice(20)
        assert 1 <= result <= 20


def test_roll_dice_single_side():
    assert roll_dice(1) == 1


def test_roll_dice_rejects_invalid_sides():
    with pytest.raises(ValueError, match="at least 1 side"):
        roll_dice(0)
    with pytest.raises(ValueError, match="at least 1 side"):
        roll_dice(-3)


def test_pick_random_item_from_list_and_tuple():
    items = ["apple", "banana", "cherry"]
    for _ in range(20):
        assert pick_random_item(items) in items
    for _ in range(20):
        assert pick_random_item(tuple(items)) in items


def test_pick_random_items_count_boundaries():
    items = ["Ada", "Lin", "Sam"]
    assert pick_random_items(items, 0) == []
    full = pick_random_items(items, 3)
    assert sorted(full) == sorted(items)
    two = pick_random_items(items, 2)
    assert len(two) == 2
    assert len(set(two)) == 2
    assert set(two).issubset(set(items))
    assert items == ["Ada", "Lin", "Sam"]


def test_shuffle_list_returns_new_list_with_same_items():
    original = [1, 2, 3, 4, 5]
    shuffled = shuffle_list(original)
    assert shuffled is not original
    assert sorted(shuffled) == original
    assert original == [1, 2, 3, 4, 5]


def test_shuffle_list_accepts_tuple_and_empty():
    assert shuffle_list([]) == []
    source = ("a", "b", "c")
    shuffled = shuffle_list(source)
    assert sorted(shuffled) == ["a", "b", "c"]
    assert source == ("a", "b", "c")


def test_generate_simple_password_default_length_and_charset():
    password = generate_simple_password()
    assert len(password) == 12
    allowed = set(string.ascii_letters + string.digits + string.punctuation)
    assert set(password).issubset(allowed)


def test_generate_simple_password_without_symbols():
    allowed = set(string.ascii_letters + string.digits)
    for length in (1, 8, 16):
        password = generate_simple_password(length, include_symbols=False)
        assert len(password) == length
        assert set(password).issubset(allowed)
        assert not set(password).intersection(string.punctuation)


def test_generate_simple_password_with_symbols(monkeypatch):
    sequence = iter("aB3$x9")
    monkeypatch.setattr(
        "py_simple_package.src.py_simple.easy_random.random.choice",
        lambda chars: next(sequence),
    )
    assert generate_simple_password(6, include_symbols=True) == "aB3$x9"


def test__simple_rejects_invalid_length():
    with pytest.raises(ValueError, match="at least 1"):
        generate_simple_password(0)
    with pytest.raises(ValueError, match="at least 1"):
        generate_simple_password(-2)


def test_random_int_inclusive_range():
    for _ in range(40):
        value = random_int(5, 15)
        assert 5 <= value <= 15
    assert random_int(7, 7) == 7


def test_random_float():
    for _ in range(50):
        val = random_float(1.5, 9.5)
        assert 1.5 <= val <= 9.5

    assert random_float(3.0, 3.0) == 3.0

    with pytest.raises(ValueError, match="start cannot be greater than end"):
        random_float(10.0, 5.0)

    with pytest.raises(ValueError, match="decimals cannot be negative"):
        random_float(1.0, 5.0, decimals=-1)


def test_random_float_with_decimals():
    for _ in range(30):
        val = random_float(0.0, 10.0, decimals=2)
        assert 0.0 <= val <= 10.0
        assert val == round(val, 2)


def test_random_float_is_available_from_public_api():
    assert public_random_float is random_float


