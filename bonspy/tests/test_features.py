from bonspy.features import _apply_operations


def test_apply_operations_domain():
    value = _apply_operations('domain', 'www.test.com')

    assert value == 'test.com'


def test_apply_operations_segment():
    value = _apply_operations('segment', 1)

    assert value == 1
