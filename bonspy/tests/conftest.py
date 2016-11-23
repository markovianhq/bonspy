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
    g.add_node(1, split='segment.age',
               state=OrderedDict([('segment', 12345)]))
    g.add_node(2, split='segment.age',
               state=OrderedDict([('segment', 67890)]))
    g.add_node(3, split='geo',
               state=OrderedDict([('segment', 12345), ('segment.age', (0., 10.))]))
    g.add_node(4, split='geo',
               state=OrderedDict([('segment', 12345), ('segment.age', (10., 20.))]))
    g.add_node(5, split='geo',
               state=OrderedDict([('segment', 67890), ('segment.age', (0., 20.))]))
    g.add_node(6, split='geo',
               state=OrderedDict([('segment', 67890), ('segment.age', (20., 40.))]))
    g.add_node(7, is_leaf=True, output=0.10,
               state=OrderedDict([('segment', 12345), ('segment.age', (0, 10.)),
                                  ('geo', ('UK', 'DE'))]))
    g.add_node(8, is_leaf=True, output=0.20,
               state=OrderedDict([('segment', 12345), ('segment.age', (0, 10.)),
                                  ('geo', ('US', 'BR'))]))
    g.add_node(9, is_leaf=True, output=0.10,
               state=OrderedDict([('segment', 12345), ('segment.age', (10., 20.)),
                                  ('geo', ('UK', 'DE'))]))
    g.add_node(10, is_leaf=True, output=0.20,
               state=OrderedDict([('segment', 12345), ('segment.age', (10., 20.)),
                                  ('geo', ('US', 'BR'))]))
    g.add_node(11, is_leaf=True, output=0.10,
               state=OrderedDict([('segment', 67890), ('segment.age', (0., 20.)),
                                  ('geo', ('UK', 'DE'))]))
    g.add_node(12, is_leaf=True, output=0.20,
               state=OrderedDict([('segment', 67890), ('segment.age', (0., 20.)),
                                  ('geo', ('US', 'BR'))]))
    g.add_node(13, is_leaf=True, output=0.10,
               state=OrderedDict([('segment', 67890), ('segment.age', (20., 40.)),
                                  ('geo', ('UK', 'DE'))]))
    g.add_node(14, is_leaf=True, output=0.20,
               state=OrderedDict([('segment', 67890), ('segment.age', (20., 40.)),
                                  ('geo', ('US', 'BR'))]))
    g.add_node(15, is_default_leaf=True, output=0.05, state=OrderedDict())
    g.add_node(16, is_default_leaf=True, output=0.05,
               state=OrderedDict([('segment', 12345)]))
    g.add_node(17, is_default_leaf=True, output=0.05,
               state=OrderedDict([('segment', 67890)]))
    g.add_node(18, is_default_leaf=True, output=0.05,
               state=OrderedDict([('segment', 12345), ('segment.age', (0., 10.))]))
    g.add_node(19, is_default_leaf=True, output=0.05,
               state=OrderedDict([('segment', 12345), ('segment.age', (10., 20.))]))
    g.add_node(20, is_default_leaf=True, output=0.05,
               state=OrderedDict([('segment', 67890), ('segment.age', (0., 20.))]))
    g.add_node(21, is_default_leaf=True, output=0.05,
               state=OrderedDict([('segment', 67890), ('segment.age', (20., 40.))]))

    g.add_edge(0, 1, value=12345, type='assignment')
    g.add_edge(0, 2, value=67890, type='assignment')
    g.add_edge(1, 3, value=(0., 10.), type='range')
    g.add_edge(1, 4, value=(10., 20.), type='range')
    g.add_edge(2, 5, value=(0., 20.), type='range')
    g.add_edge(2, 6, value=(20., 40.), type='range')
    g.add_edge(3, 7, value=('UK', 'DE'), type='membership')
    g.add_edge(3, 8, value=('US', 'BR'), type='membership')
    g.add_edge(4, 9, value=('UK', 'DE'), type='membership')
    g.add_edge(4, 10, value=('US', 'BR'), type='membership')
    g.add_edge(5, 11, value=('UK', 'DE'), type='membership')
    g.add_edge(5, 12, value=('US', 'BR'), type='membership')
    g.add_edge(6, 13, value=('UK', 'DE'), type='membership')
    g.add_edge(6, 14, value=('US', 'BR'), type='membership')
    g.add_edge(0, 15)
    g.add_edge(1, 16)
    g.add_edge(2, 17)
    g.add_edge(3, 18)
    g.add_edge(4, 19)
    g.add_edge(5, 20)
    g.add_edge(6, 21)

    return g


@pytest.fixture
def graph_two_range_features():
    g = nx.DiGraph()

    g.add_node(0, split=('segment', 'segment.age'), state={})
    g.add_node(1, split='user_hour', state={'segment': 12345, 'segment.age': (0., 10.)})
    g.add_node(2, split='user_hour', state={'segment': 12345, 'segment.age': (10., 20.)})
    g.add_node(3, split='user_hour', state={'segment': 67890, 'segment.age': (0., 20.)})
    g.add_node(4, split='user_hour', state={'segment': 67890, 'segment.age': (20., 40.)})
    g.add_node(5, is_leaf=True, output=0.10,
               state={'segment': 12345, 'segment.age': (0, 10.),
                      'user_hour': (0., 12.)})
    g.add_node(6, is_leaf=True, output=0.20,
               state={'segment': 12345, 'segment.age': (0, 10.),
                      'user_hour': (12., 100.)})
    g.add_node(7, is_leaf=True, output=0.10,
               state={'segment': 12345, 'segment.age': (10., 20.),
                      'user_hour': (0., 12.)})
    g.add_node(8, is_leaf=True, output=0.20,
               state={'segment': 12345, 'segment.age': (10., 20.),
                      'user_hour': (12., 100.)})
    g.add_node(9, is_leaf=True, output=0.10,
               state={'segment': 67890, 'segment.age': (0., 20.),
                      'user_hour': (0., 12.)})
    g.add_node(10, is_leaf=True, output=0.20,
               state={'segment': 67890, 'segment.age': (0., 20.),
                      'user_hour': (12., 100.)})
    g.add_node(11, is_leaf=True, output=0.10,
               state={'segment': 67890, 'segment.age': (20., 40.),
                      'user_hour': (0., 12.)})
    g.add_node(12, is_leaf=True, output=0.20,
               state={'segment': 67890, 'segment.age': (20., 40.),
                      'user_hour': (12., 100.)})
    g.add_node(13, is_default_leaf=True, output=0.05, state={})
    g.add_node(14, is_default_leaf=True, output=0.05, state={'segment': 12345})
    g.add_node(15, is_default_leaf=True, output=0.05, state={'segment': 67890})
    g.add_node(16, is_default_leaf=True, output=0.05,
               state={'segment': 12345, 'segment.age': (0., 10.)})
    g.add_node(17, is_default_leaf=True, output=0.05,
               state={'segment': 12345, 'segment.age': (10., 20.)})
    g.add_node(18, is_default_leaf=True, output=0.05,
               state={'segment': 67890, 'segment.age': (0., 20.)})
    g.add_node(19, is_default_leaf=True, output=0.05,
               state={'segment': 67890, 'segment.age': (20., 40.)})

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

    g.add_node(0, split='geo', state={})
    g.add_node(1, split=('site_id', 'placement_id'), state={'geo': 'DE'})
    g.add_node(2, split=('site_id', 'placement_id'), state={'geo': 'UK'})
    g.add_node(
        3, state={'geo': 'DE', 'site_id': 1, 'placement_id': 'a'},
        split='os'
    )
    g.add_node(
        4, is_leaf=True, output=.4,
        state={'geo': 'DE', 'site_id': 1, 'placement_id': 'b'}
    )
    g.add_node(
        5, state={'geo': 'UK', 'site_id': 1, 'placement_id': 'a'},
        split='os'
    )
    g.add_node(
        6, is_leaf=True, output=.6,
        state={'geo': 'UK', 'site_id': 1, 'placement_id': 'b'}
    )
    g.add_node(
        7, is_leaf=True, output=.9,
        state={'geo': 'UK', 'site_id': 2, 'placement_id': 'a'}
    )
    g.add_node(
        8, is_leaf=True, output=.2,
        state={'geo': 'DE', 'site_id': 1, 'placement_id': 'a', 'os': 'linux'}
    )
    g.add_node(
        9, is_leaf=True, output=.3,
        state={'geo': 'UK', 'site_id': 1, 'placement_id': 'a', 'os': 'windows'}
    )
    g.add_node(
        10, is_default_leaf=True, output=.1, state={}
    )
    g.add_node(
        11, is_default_leaf=True, output=.5, state={'geo': 'DE'}
    )
    g.add_node(
        12, is_default_leaf=True, output=.05, state={'geo': 'UK'}
    )
    g.add_node(
        13, is_default_leaf=True, output=.2, state={'geo': 'DE', 'site_id': 1, 'placement_id': 'a'}
    )
    g.add_node(
        14, is_default_leaf=True, output=.3, state={'geo': 'UK', 'site_id': 1, 'placement_id': 'a'}
    )

    g.add_edge(0, 1, value='DE', type='assignment')
    g.add_edge(0, 2, value='UK', type='assignment')
    g.add_edge(1, 3, value=(1, 'a'), type=('assignment', 'assignment'))
    g.add_edge(1, 4, value=(1, 'b'), type=('assignment', 'assignment'))
    g.add_edge(2, 5, value=(1, 'a'), type=('assignment', 'assignment'))
    g.add_edge(2, 6, value=(1, 'b'), type=('assignment', 'assignment'))
    g.add_edge(2, 7, value=(2, 'a'), type=('assignment', 'assignment'))
    g.add_edge(3, 8, value='linux', type='assignment')
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

    g.add_node(0, split='geo', state={})
    g.add_node(1, split=('site_id', 'placement_id'), state={'geo': 'DE'})
    g.add_node(2, is_default_node=True, split=('site_id', 'placement_id'), state={})
    g.add_node(
        3, state={'geo': 'DE', 'site_id': 1, 'placement_id': 'a'},
        split='os'
    )
    g.add_node(
        4, is_leaf=True, output=.4,
        state={'geo': 'DE', 'site_id': 1, 'placement_id': 'b'}
    )
    g.add_node(
        5, state={'site_id': 1, 'placement_id': 'a'},
        split='os'
    )
    g.add_node(
        6, is_leaf=True, output=.6,
        state={'site_id': 1, 'placement_id': 'b'}
    )
    g.add_node(
        7, is_leaf=True, output=.9,
        state={'site_id': 2, 'placement_id': 'a'}
    )
    g.add_node(
        8, is_leaf=True, output=.2,
        state={'geo': 'DE', 'site_id': 1, 'placement_id': 'a', 'os': 'linux'}
    )
    g.add_node(
        9, is_leaf=True, output=.3,
        state={'site_id': 1, 'placement_id': 'a', 'os': 'windows'}
    )
    g.add_node(
        10, is_default_leaf=True, output=.5, state={'geo': 'DE'}
    )
    g.add_node(
        11, is_default_leaf=True, output=.05, state={'geo': 'UK'}
    )
    g.add_node(
        12, is_default_leaf=True, output=.2, state={'geo': 'DE', 'site_id': 1, 'placement_id': 'a'}
    )
    g.add_node(
        13, is_default_leaf=True, output=.3, state={'site_id': 1, 'placement_id': 'a'}
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


@pytest.fixture(params=['graph', 'graph_two_range_features', 'graph_compound_feature', 'graph_with_default_node'])
def parameterized_graph(request):
    return request.getfuncargvalue(request.param)
