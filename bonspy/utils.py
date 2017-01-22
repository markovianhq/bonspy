def compare_vectors(x, y):
    for x_i, y_i in zip(x, y):
        comparison = _compare(x_i, y_i)
        if comparison == 0:
            continue
        else:
            return comparison
    return 0


def _compare(x, y):
    if x is not None and y is not None:
        return int(x > y) - int(x < y)
    elif x is not None and y is None:
        return -1
    elif x is None and y is not None:
        return 1
    else:
        return 0


def is_absent_value(value):
    return value in (None, '', (), [])
