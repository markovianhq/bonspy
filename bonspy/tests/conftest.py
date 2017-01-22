# -*- coding: utf-8 -*-

from __future__ import (
    print_function, division, generators,
    absolute_import, unicode_literals
)

from collections import OrderedDict

import networkx as nx

import pytest


@pytest.fixture
def graph():
    g = nx.DiGraph()

    g.add_node(0, split='segment', state=OrderedDict())
    g.add_node(1, split=OrderedDict([(4, 'segment.age'), (26, 'browser'), (5, 'language')]),
               state=OrderedDict([('segment', 12345)]))
    g.add_node(2, split='segment.age',
               state=OrderedDict([('segment', 67890)]))
    g.add_node(3, split='geo',
               state=OrderedDict([('segment', 13579)]))
    g.add_node(4, split='geo',
               state=OrderedDict([('segment', 12345), ('segment.age', (-float('inf'), 10.))]))
    g.add_node(5, split='geo',
               state=OrderedDict([('segment', 12345), ('language', 'english')]))
    g.add_node(6, split=OrderedDict([(14, 'os'), (15, 'geo')]),
               state=OrderedDict([('segment', 67890), ('segment.age', (-float('inf'), 20.))]))
    g.add_node(7, split='geo',
               state=OrderedDict([('segment', 67890), ('segment.age', (20., 40.))]))
    g.add_node(26, is_leaf=True, output=1.1,
               state=OrderedDict([('segment', 12345), ('browser', 'safari')]))
    g.add_node(8, is_leaf=True, output=0.13,
               state=OrderedDict([('segment', 13579),
                                  ('geo', ('UK', 'DE', 'US'))]))
    g.add_node(9, is_leaf=True, output=1.2,
               state=OrderedDict([('segment', 13579),
                                  ('geo', ('BR',))]))
    g.add_node(10, is_leaf=True, output=0.10,
               state=OrderedDict([('segment', 12345), ('segment.age', (0, 10.)),
                                  ('geo', ('UK', 'DE'))]))
    g.add_node(11, is_leaf=True, output=0.20,
               state=OrderedDict([('segment', 12345), ('segment.age', (0, 10.)),
                                  ('geo', None)]))
    g.add_node(12, is_leaf=True, output=0.10,
               state=OrderedDict([('segment', 12345), ('segment.age', (10., 20.)),
                                  ('geo', ('UK', 'DE'))]))
    g.add_node(13, is_leaf=True, output=0.20,
               state=OrderedDict([('segment', 12345), ('segment.age', (10., 20.)),
                                  ('geo', ('US', 'BR'))]))
    g.add_node(14, is_leaf=True, is_smart=True, value=0.,
               state=OrderedDict([('segment', 67890), ('segment.age', (0., 20.)),
                                  ('os', 'windows')]))
    g.add_node(15, is_leaf=True, output=0.20,
               state=OrderedDict([('segment', 67890), ('segment.age', (0., 20.)),
                                  ('geo', ('US', 'BR'))]))
    g.add_node(16, is_leaf=True, is_smart=True, value=0.10,
               state=OrderedDict([('segment', 67890), ('segment.age', (20., float('inf'))),
                                  ('geo', ('UK', 'DE'))]))
    g.add_node(17, is_leaf=True, is_smart=True,
               input_field='uniform', offset=0.4, max_value=1.,
               state=OrderedDict([('segment', 67890), ('segment.age', (20., 40.)),
                                  ('geo', None)]))
    g.add_node(18, is_default_leaf=True, output=0.05, state=OrderedDict())
    g.add_node(19, is_default_leaf=True, is_smart=True,
               input_field='uniform', multiplier=1.2, min_value=1.,
               state=OrderedDict([('segment', 12345)]))
    g.add_node(20, is_default_leaf=True, is_smart=True, leaf_name='default_17',
               input_field='uniform', multiplier=.32, max_value=3.1,
               state=OrderedDict([('segment', 67890)]))
    g.add_node(21, is_default_leaf=True, output=0.09,
               state=OrderedDict([('segment', 13579)]))
    g.add_node(22, is_default_leaf=True, output=0.05,
               state=OrderedDict([('segment', 12345), ('segment.age', (0., 10.))]))
    g.add_node(23, is_default_leaf=True, output=0.05,
               state=OrderedDict([('segment', 12345), ('segment.age', (10., 20.))]))
    g.add_node(24, is_default_leaf=True, output=0.05,
               state=OrderedDict([('segment', 67890), ('segment.age', (0., 20.))]))
    g.add_node(25, is_default_leaf=True, output=0.05,
               state=OrderedDict([('segment', 67890), ('segment.age', (20., 40.))]))

    g.add_edge(0, 1, value=12345, type='assignment')
    g.add_edge(0, 2, value=67890, type='assignment')
    g.add_edge(0, 3, value=13579, type='assignment')
    g.add_edge(1, 4, value=(0., 10.), type='range')
    g.add_edge(1, 5, value='english', type='assignment')
    g.add_edge(1, 26, value='safari', type='assignment')
    g.add_edge(2, 6, value=(0., 20.), type='range')
    g.add_edge(2, 7, value=(20., 40.), type='range')
    g.add_edge(3, 8, value=('UK', 'DE', 'US'), type='membership')
    g.add_edge(3, 9, value=('BR',), type='membership')
    g.add_edge(4, 10, value=('UK', 'DE'), type='membership')
    g.add_edge(4, 11, value=None, type='membership')
    g.add_edge(5, 12, value=('UK', 'DE'), type='membership')
    g.add_edge(5, 13, value=('US', 'BR'), type='membership')
    g.add_edge(6, 14, value='windows', type='assignment')
    g.add_edge(6, 15, value=('US', 'BR'), type='membership')
    g.add_edge(7, 16, value=('UK', 'DE'), type='membership')
    g.add_edge(7, 17, value=None, type='membership')
    g.add_edge(0, 18)
    g.add_edge(1, 19)
    g.add_edge(2, 20)
    g.add_edge(3, 21)
    g.add_edge(4, 22)
    g.add_edge(5, 23)
    g.add_edge(6, 24)
    g.add_edge(7, 25)

    return g


@pytest.fixture
def graph_two_range_features():
    g = nx.DiGraph()

    g.add_node(0, split=('segment', 'segment.age'), state=OrderedDict())
    g.add_node(1, split='user_hour', state=OrderedDict([('segment', 12345), ('segment.age', (0., 10.))]))
    g.add_node(2, split='user_hour', state=OrderedDict([('segment', 12345), ('segment.age', (10., 20.))]))
    g.add_node(3, split='user_hour', state=OrderedDict([('segment', 67890), ('segment.age', (0., 20.))]))
    g.add_node(4, split='user_hour', state=OrderedDict([('segment', 67890), ('segment.age', (20., 40.))]))
    g.add_node(5, is_leaf=True, output=0.10,
               state=OrderedDict([
                   ('segment', 12345),
                   ('segment.age', (0, 10.)),
                   ('user_hour', (0., 12.))
               ]))
    g.add_node(6, is_leaf=True, output=0.20,
               state=OrderedDict([
                   ('segment', 12345),
                   ('segment.age', (0, 10.)),
                   ('user_hour', (12., 100.))
               ]))
    g.add_node(7, is_leaf=True, output=0.10,
               state=OrderedDict([
                   ('segment', 12345),
                   ('segment.age', (10., 20.)),
                   ('user_hour', (0., 12.))
               ]))
    g.add_node(8, is_leaf=True, output=0.20,
               state=OrderedDict([
                   ('segment', 12345),
                   ('segment.age', (10., 20.)),
                   ('user_hour', (12., 100.))
               ]))
    g.add_node(9, is_leaf=True, output=0.10,
               state=OrderedDict([
                   ('segment', 67890),
                   ('segment.age', (0., 20.)),
                   ('user_hour', (0., 12.))
               ]))
    g.add_node(10, is_leaf=True, output=0.20,
               state=OrderedDict([
                   ('segment', 67890),
                   ('segment.age', (0., 20.)),
                   ('user_hour', (12., 100.))
               ]))
    g.add_node(11, is_leaf=True, output=0.10,
               state=OrderedDict([
                   ('segment', 67890),
                   ('segment.age', (20., 40.)),
                   ('user_hour', (0., 12.))
               ]))
    g.add_node(12, is_leaf=True, output=0.20,
               state=OrderedDict([
                   ('segment', 67890),
                   ('segment.age', (20., 40.)),
                   ('user_hour', (12., 100.))
               ]))
    g.add_node(13, is_default_leaf=True, output=0.05, state=OrderedDict())
    g.add_node(14, is_default_leaf=True, output=0.05, state=OrderedDict([('segment', 12345)]))
    g.add_node(15, is_default_leaf=True, output=0.05, state=OrderedDict([('segment', 67890)]))
    g.add_node(16, is_default_leaf=True, output=0.05,
               state=OrderedDict([('segment', 12345), ('segment.age', (0., 10.))]))
    g.add_node(17, is_default_leaf=True, output=0.05,
               state=OrderedDict([('segment', 12345), ('segment.age', (10., 20.))]))
    g.add_node(18, is_default_leaf=True, output=0.05,
               state=OrderedDict([('segment', 67890), ('segment.age', (0., 20.))]))
    g.add_node(19, is_default_leaf=True, output=0.05,
               state=OrderedDict([('segment', 67890), ('segment.age', (20., 40.))]))

    g.add_edge(0, 1, value=(12345, (0., 10.)), type=('assignment', 'range'))
    g.add_edge(0, 2, value=(12345, (10., 20.)), type=('assignment', 'range'))
    g.add_edge(0, 3, value=(67890, (0., 20.)), type=('assignment', 'range'))
    g.add_edge(0, 4, value=(67890, (20., 40.)), type=('assignment', 'range'))
    g.add_edge(1, 5, value=(0., 12.), type='range')
    g.add_edge(1, 6, value=(12., 100.), type='range')
    g.add_edge(2, 7, value=(0., 12.), type='range')
    g.add_edge(2, 8, value=(12., 100.), type='range')
    g.add_edge(3, 9, value=(0., 12.), type='range')
    g.add_edge(3, 10, value=(12., 100.), type='range')
    g.add_edge(4, 11, value=(0., 12.), type='range')
    g.add_edge(4, 12, value=(12., 100.), type='range')
    g.add_edge(0, 13)
    g.add_edge(1, 16)
    g.add_edge(2, 17)
    g.add_edge(3, 18)
    g.add_edge(4, 19)

    return g


@pytest.fixture
def graph_compound_feature():
    g = nx.DiGraph()

    g.add_node(0, split='geo', state=OrderedDict())
    g.add_node(1, split=('site_id', 'placement_id'), state=OrderedDict([('geo', 'DE')]))
    g.add_node(2, split=('site_id', 'placement_id'), state=OrderedDict([('geo', 'UK')]))
    g.add_node(
        3, state=OrderedDict([('geo', 'DE'), ('site_id', 1), ('placement_id', 'a')]),
        split='os'
    )
    g.add_node(
        4, is_leaf=True, output=.4,
        state=OrderedDict([('geo', 'DE'), ('site_id', 1), ('placement_id', 'b')])
    )
    g.add_node(
        5, state=OrderedDict([('geo', 'UK'), ('site_id', 1), ('placement_id', 'a')]),
        split='os'
    )
    g.add_node(
        6, is_leaf=True, output=.6,
        state=OrderedDict([('geo', 'UK'), ('site_id', 1), ('placement_id', 'b')])
    )
    g.add_node(
        7, is_leaf=True, output=.9,
        state=OrderedDict([('geo', 'UK'), ('site_id', 2), ('placement_id', 'a')])
    )
    g.add_node(
        8, is_leaf=True, output=.2,
        state=OrderedDict([('geo', 'DE'), ('site_id', 1), ('placement_id', 'a'), ('os', 'linux')])
    )
    g.add_node(
        15, is_leaf=True, output=.1,
        state=OrderedDict([('geo', 'DE'), ('site_id', 1), ('placement_id', 'a'), ('os', 'windows')])
    )
    g.add_node(
        9, is_leaf=True, output=.3,
        state=OrderedDict([('geo', 'UK'), ('site_id', 2), ('placement_id', 'a'), ('os', 'windows')])
    )
    g.add_node(
        10, is_default_leaf=True, output=.1, state=OrderedDict()
    )
    g.add_node(
        11, is_default_leaf=True, output=.5, state=OrderedDict([('geo', 'DE')])
    )
    g.add_node(
        12, is_default_leaf=True, output=.05, state=OrderedDict([('geo', 'UK')])
    )
    g.add_node(
        13, is_default_leaf=True, output=.2, state=OrderedDict([('geo', 'DE'), ('site_id', 1), ('placement_id', 'a')])
    )
    g.add_node(
        14, is_default_leaf=True, output=.3, state=OrderedDict([('geo', 'UK'), ('site_id', 1), ('placement_id', 'a')])
    )

    g.add_edge(0, 1, value='DE', type='assignment')
    g.add_edge(0, 2, value='UK', type='assignment')
    g.add_edge(1, 3, value=(1, 'a'), type=('assignment', 'assignment'))
    g.add_edge(1, 4, value=(1, 'b'), type=('assignment', 'assignment'))
    g.add_edge(2, 5, value=(1, 'a'), type=('assignment', 'assignment'))
    g.add_edge(2, 6, value=(1, 'b'), type=('assignment', 'assignment'))
    g.add_edge(2, 7, value=(2, 'a'), type=('assignment', 'assignment'))
    g.add_edge(3, 8, value='linux', type='assignment')
    g.add_edge(3, 15, value='windows', type='assignment')
    g.add_edge(5, 9, value='windows', type='assignment')
    g.add_edge(0, 10)
    g.add_edge(1, 11)
    g.add_edge(2, 12)
    g.add_edge(3, 13)
    g.add_edge(5, 14)

    return g


@pytest.fixture
def graph_with_default_node():
    g = nx.DiGraph()

    g.add_node(0, split='geo', state=OrderedDict())
    g.add_node(1, split=('site_id', 'placement_id'), state=OrderedDict([('geo', 'DE')]))
    g.add_node(2, is_default_node=True, split=('site_id', 'placement_id'), state=OrderedDict())
    g.add_node(
        3, state=OrderedDict([('geo', 'DE'), ('site_id', 1), ('placement_id', 'a')]),
        split='os'
    )
    g.add_node(
        4, is_leaf=True, output=.4,
        state=OrderedDict([('geo', 'DE'), ('site_id', 1), ('placement_id', 'b')])
    )
    g.add_node(
        5, state=OrderedDict([('site_id', 1), ('placement_id', 'a')]),
        split='os'
    )
    g.add_node(
        6, is_leaf=True, output=.6,
        state=OrderedDict([('site_id', 1), ('placement_id', 'b')])
    )
    g.add_node(
        7, is_leaf=True, output=.9,
        state=OrderedDict([('site_id', 2), ('placement_id', 'a')])
    )
    g.add_node(
        8, is_leaf=True, output=.2,
        state=OrderedDict([('geo', 'DE'), ('site_id', 1), ('placement_id', 'a'), ('os', 'linux')])
    )
    g.add_node(
        9, is_leaf=True, output=.3,
        state=OrderedDict([('site_id', 1), ('placement_id', 'a'), ('os', 'windows')])
    )
    g.add_node(
        10, is_default_leaf=True, output=.5, state=OrderedDict([('geo', 'DE')])
    )
    g.add_node(
        11, is_default_leaf=True, output=.05, state=OrderedDict([('geo', 'UK')])
    )
    g.add_node(
        12, is_default_leaf=True, output=.2, state=OrderedDict([('geo', 'DE'), ('site_id', 1), ('placement_id', 'a')])
    )
    g.add_node(
        13, is_default_leaf=True, output=.3, state=OrderedDict([('site_id', 1), ('placement_id', 'a')])
    )

    g.add_edge(0, 1, value='DE', type='assignment')
    g.add_edge(0, 2)
    g.add_edge(1, 3, value=(1, 'a'), type=('assignment', 'assignment'))
    g.add_edge(1, 4, value=(1, 'b'), type=('assignment', 'assignment'))
    g.add_edge(2, 5, value=(1, 'a'), type=('assignment', 'assignment'))
    g.add_edge(2, 6, value=(1, 'b'), type=('assignment', 'assignment'))
    g.add_edge(2, 7, value=(2, 'a'), type=('assignment', 'assignment'))
    g.add_edge(3, 8, value='linux', type='assignment')
    g.add_edge(5, 9, value='windows', type='assignment')
    g.add_edge(1, 10)
    g.add_edge(2, 11)
    g.add_edge(3, 12)
    g.add_edge(5, 13)

    return g


@pytest.fixture
def small_graph():
    g = nx.DiGraph()

    g.add_node(0, split='user_hour', state=OrderedDict())
    g.add_node(1, split='user_day',
               state=OrderedDict([('user_hour', (None, 10))]))

    g.add_node(2, split=OrderedDict([(5, 'user_day'), (6, 'os')]),
               state=OrderedDict([('user_hour', (11.3, 15))]))

    g.add_node(3, is_leaf=True, output=1.3,
               state=OrderedDict([('user_hour', (None, 10)), ('user_day', (1, 4))]))

    g.add_node(4, is_leaf=True, output=1.4,
               state=OrderedDict([('user_hour', (None, 10)), ('user_day', (5, 6))]))

    g.add_node(5, is_leaf=True, output=1.5,
               state=OrderedDict([('user_hour', (11.3, 15)), ('user_day', (3, 6))]))

    g.add_node(6, is_leaf=True, output=1.6,
               state=OrderedDict([('user_hour', (11.3, 15)), ('os', 'linux')]))

    g.add_node(7, is_default_leaf=True, output=0.7, state=OrderedDict())
    g.add_node(8, is_default_leaf=True, output=0.8, state=OrderedDict([('user_hour', (None, 10))]))
    g.add_node(9, is_default_leaf=True, output=0.9, state=OrderedDict([('user_hour', (11.3, 15))]))

    g.add_edge(0, 1, value=(None, 10), type='range')
    g.add_edge(0, 2, value=(11.3, 15), type='range')
    g.add_edge(1, 3, value=(1, 4), type='range')
    g.add_edge(1, 4, value=(5, 6), type='range')
    g.add_edge(2, 5, value=(3, 6), type='range')
    g.add_edge(2, 6, value='linux', type='assignment')
    g.add_edge(0, 7)
    g.add_edge(1, 8)
    g.add_edge(2, 9)

    return g


@pytest.fixture(params=['graph', 'graph_two_range_features', 'graph_compound_feature',
                        'graph_with_default_node', 'small_graph'])
def parameterized_graph(request):
    return request.getfuncargvalue(request.param)


@pytest.fixture
def missing_values_graph():
    g = nx.DiGraph()

    g.add_node('root', split='segment', state=OrderedDict())
    g.add_node(
        'root_default',
        is_default_leaf=True,
        state=OrderedDict(),
        output=.1
    )
    g.add_node('segment_1', split='segment.age', state=OrderedDict([('segment', 1)]))
    g.add_node(
        'segment_1_default',
        is_default_leaf=True,
        state=OrderedDict([('segment', 1)]),
        output=.1
    )
    g.add_node('segment_2', split='os', state=OrderedDict([('segment', 2)]))
    g.add_node(
        'segment_2_default',
        is_default_leaf=True,
        state=OrderedDict([('segment', 2)]),
        output=.1
    )
    g.add_node('segment_missing', split='segment.age', state=OrderedDict([('segment', None)]))
    g.add_node(
        'segment_missing_default',
        is_default_leaf=True,
        state=OrderedDict([('segment', None)]),
        output=.1
    )
    g.add_node(
        'segment_1_age_lower',
        is_leaf=True,
        state=OrderedDict([('segment', 1), ('segment.age', (-float('inf'), 10.))]),
        output=.1
    )
    g.add_node(
        'segment_1_age_upper',
        is_leaf=True,
        state=OrderedDict([('segment', 1), ('segment.age', (10., float('inf')))]),
        output=.1
    )
    g.add_node(
        'segment_2_os_known',
        is_leaf=True,
        state=OrderedDict([('segment', 2), ('os', ('linux', 'osx'))]),
        output=.1
    )
    g.add_node(
        'segment_2_os_unknown',
        is_leaf=True,
        state=OrderedDict([('segment', 2), ('os', None)]),
        output=.1
    )
    g.add_node(
        'segment_missing_age_missing',
        split='os',
        state=OrderedDict([('segment', None), ('segment.age', None)])
    )
    g.add_node(
        'segment_missing_age_missing_default',
        is_default_leaf=True,
        state=OrderedDict([('segment', None), ('segment.age', None)]),
        output=.1
    )
    g.add_node(
        'segment_missing_age_missing_os_known',
        is_leaf=True,
        state=OrderedDict([('segment', None), ('segment.age', None), ('os', ('linux',))]),
        output=.1
    )

    g.add_edge('root', 'segment_1', value=1, type='assignment')
    g.add_edge('root', 'segment_2', value=2, type='assignment')
    g.add_edge('root', 'segment_missing', value=None, type='assignment')
    g.add_edge('root', 'root_default')

    g.add_edge(
        'segment_1',
        'segment_1_age_lower',
        value=(-float('inf'), 10.),
        type='range'
    )
    g.add_edge(
        'segment_1',
        'segment_1_age_upper',
        value=(10., float('inf')),
        type='range'
    )
    g.add_edge(
        'segment_1',
        'segment_1_default'
    )

    g.add_edge(
        'segment_2',
        'segment_2_os_known',
        value=('linux', 'osx'),
        type='membership'
    )
    g.add_edge(
        'segment_2',
        'segment_2_os_unknown',
        value=None,
        type='membership'
    )
    g.add_edge(
        'segment_2',
        'segment_2_default'
    )

    g.add_edge(
        'segment_missing',
        'segment_missing_age_missing',
        value=None,
        type='range'
    )
    g.add_edge(
        'segment_missing',
        'segment_missing_default'
    )

    g.add_edge(
        'segment_missing_age_missing',
        'segment_missing_age_missing_os_known',
        value=('linux',),
        type='membership'
    )

    g.add_edge(
        'segment_missing_age_missing',
        'segment_missing_age_missing_default'
    )

    return g


@pytest.fixture
def negated_values_graph():
    g = nx.DiGraph()

    g.add_node('root', split=OrderedDict([
        ('every_segment', ('segment', 'segment')),
        ('negated_every_segment', ('segment', 'segment', 'segment')),
        ('any_segment', ('segment', 'segment')),
        ('negated_any_segment', ('segment', 'segment'))
    ]), state=OrderedDict())

    g.add_node(
        'every_segment',
        is_leaf=True,
        output=0.1,
        state=OrderedDict([(('segment', 'segment'), (1, 2))])
    )

    g.add_node(
        'negated_every_segment',
        is_leaf=True,
        output=0.1,
        state=OrderedDict([(('segment', 'segment', 'segment'), (1, 2, 3))])
    )

    g.add_node(
        'any_segment',
        is_leaf=True,
        output=0.1,
        state=OrderedDict([(('segment', 'segment'), (1, 2))])
    )

    g.add_node(
        'negated_any_segment',
        is_leaf=True,
        output=0.1,
        state=OrderedDict([(('segment', 'segment'), (1, 10))])
    )

    g.add_edge(
        'root',
        'every_segment',
        value=(1, 2),
        type=('assignment', 'assignment')
    )

    g.add_edge(
        'root',
        'negated_every_segment',
        value=(1, 2, 3),
        type=('assignment', 'assignment', 'assignment'),
        is_negated=(False, True, False)
    )

    g.add_edge(
        'root',
        'any_segment',
        value=(1, 2),
        type=('assignment', 'assignment'),
        join_statement='any'
    )

    g.add_edge(
        'root',
        'negated_any_segment',
        value=(1, 10),
        type=('assignment', 'assignment'),
        join_statement='any',
        is_negated=(False, True)
    )

    return g
