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


class ConstantDict(dict):
    def __init__(self, constant):
        super(ConstantDict, self).__init__()
        self.constant = constant

    def values(self):
        return [self.constant]

    def __delitem__(self, key):
        try:
            super(ConstantDict, self).__delitem__(key)
        except KeyError:
            pass

    def __eq__(self, other):
        if type(other) is not type(self):
            return False
        elif other.constant == self.constant:
            return True
        else:
            return False

    def __getitem__(self, item):
        try:
            return super(ConstantDict, self).__getitem__(item)
        except KeyError:
            return self.constant

    def __repr__(self):
        return 'ConstantDict({})'.format(self.constant)
