import pytest

from chob_tools.data_structures.invertible_dict import InvertibleDict


def test_empty_dict():
    invertible_dict = InvertibleDict()
    assert len(invertible_dict) == 0
    assert len(invertible_dict.inv) == 0


def test_non_empty_dict():
    food_dict = {'apple': 'fruit', 'carrot': 'vegetable'}
    invertible_dict = InvertibleDict(food_dict)
    assert len(invertible_dict) == 2
    assert len(invertible_dict.inv) == 2


def test_non_empty_dict_duplicate_values():
    food_dict = {'apple': 'fruit', 'carrot': 'vegetable', 'peach': 'fruit'}
    with pytest.raises(ValueError):
        invertible_dict = InvertibleDict(food_dict)


def test_add_retrieve_update_item():
    invertible_dict = InvertibleDict()

    # Add and retrieve item
    invertible_dict['apple'] = 'fruit'
    assert invertible_dict['apple'] == 'fruit'
    assert invertible_dict.inv['fruit'] == 'apple'

    # Update invertible dict 'apple' key
    invertible_dict['apple'] = 'food'
    assert invertible_dict['apple'] == 'food'
    assert 'fruit' not in invertible_dict.inv
    assert invertible_dict.inv['food'] == 'apple'


def test_duplicate_value():
    invertible_dict = InvertibleDict()
    invertible_dict['apple'] = 'fruit'
    with pytest.raises(ValueError):
        invertible_dict['orange'] = 'fruit'

    # Check for inverted dict
    with pytest.raises(ValueError):
        invertible_dict.inv['food'] = 'apple'


def test_iteration():
    invertible_dict = InvertibleDict()
    invertible_dict['apple'] = 'fruit'
    invertible_dict['carrot'] = 'vegetable'
    keys = list(invertible_dict)
    assert 'apple' in keys
    assert 'carrot' in keys


def test_deletion():
    invertible_dict = InvertibleDict()
    invertible_dict['apple'] = 'fruit'
    del invertible_dict['apple']
    assert 'apple' not in invertible_dict
    assert 'fruit' not in invertible_dict.inv
