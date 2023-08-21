import pytest

from chob_tools.data_structures.invertible_dict import InvertibleDict


def test_empty_dict():
    invertible_dict = InvertibleDict()
    assert len(invertible_dict) == 0


def test_add_and_retrieve_item():
    invertible_dict = InvertibleDict()
    invertible_dict['apple'] = 'fruit'
    assert invertible_dict['apple'] == 'fruit'


def test_duplicate_value():
    invertible_dict = InvertibleDict()
    invertible_dict['apple'] = 'fruit'
    with pytest.raises(ValueError):
        invertible_dict['orange'] = 'fruit'


def test_invertibility():
    invertible_dict = InvertibleDict()
    invertible_dict['apple'] = 'fruit'
    inverted_dict = invertible_dict.inv
    assert inverted_dict['fruit'] == 'apple'


def test_invertibility_with_duplicates():
    invertible_dict = InvertibleDict()
    invertible_dict['apple'] = 'fruit'
    with pytest.raises(ValueError):
        inverted_dict = invertible_dict.inv


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
    assert len(invertible_dict) == 0
