# -*- coding: utf-8 -*-

from __future__ import (
    print_function, division, generators,
    absolute_import, unicode_literals
)

from itertools import product

objects = ['advertiser', 'line_item', 'campaign']
attributes = ['recency', 'day_frequency', 'lifetime_frequency']
compound_features = objects + ['segment']

FLOORS = {
    'age': 0,
    'user_hour': 0,
    'segment.value': 1
}

CEILINGS = {
    'user_hour': 23
}

TYPES = {
    'segment': int,
    'segment.age': int,
    'segment.value': int,
    'user_hour': int
}

TYPES.update({'{object}.{attribute}'.format(object=k, attribute=v): int for (k, v) in product(objects, attributes)})


def get_validated(feature, value):
    """
    Returns the passed feature value or collection of feature values
    clamped to expected ceilings and floors.
    Further casts feature values to their expected data types.

    :param feature: str, Name of the feature
    :param value: Either one feature value or a tuple / list of feature values.
    :return: The return value has the same dimensionality as the input `value`.
    """

    if isinstance(value, (list, tuple)):
        orig_type = type(value)
        value = list(value)
        for index, a_value in enumerate(value):
            value[index] = _get_valid_value(feature, a_value)
        value = orig_type(value)
        return value
    else:
        return _get_valid_value(feature, value)


def _get_valid_value(feature, value):
    value = _get_ceiling(feature, value)
    value = _get_floor(feature, value)
    value = _type_cast(feature, value)

    return value


def _get_ceiling(feature, value):
    try:
        return min(CEILINGS[feature], value)
    except KeyError:
        return value
    except TypeError:
        # `value` is None, return None for open intervals
        return value


def _get_floor(feature, value):
    try:
        return max(FLOORS[feature], value)
    except KeyError:
        return value
    except TypeError:
        # `value` is None, return None for open intervals
        return value


def _type_cast(feature, value):
    try:
        return TYPES[feature](value)
    except KeyError:
        return value
    except TypeError:
        # `value` is None
        return value
