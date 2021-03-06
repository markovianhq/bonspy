# -*- coding: utf-8 -*-

from __future__ import (
    print_function, division, generators,
    absolute_import, unicode_literals
)

from collections import deque
import networkx as nx
import pytest
import re

from bonspy import BonsaiTree


def test_switch_header(graph):
    tree = BonsaiTree(graph)
    text = tree.bonsai.replace('\t', '').split('\n')
    switch_header_nodes = [d for _, d in tree.nodes_iter(data=True) if d.get('split') is not None and
                           set(d.get('split').values()) == {'segment.age'}]

    assert len(switch_header_nodes) == 1
    assert all([d.get('switch_header') is not None for d in switch_header_nodes])

    for row in text:
        if '.age' in row and 'segment[67890]' in row:
            assert row in {'switch segment[67890].age:'}
        elif '.age' in row and 'segment[12345]' in row:
            assert row not in {'switch segment[12345].age:'}
            assert 'elif' in row or 'if' in row


def test_switch_indent(graph):
    tree = BonsaiTree(graph)

    switch_header_nodes = [n for n, d in tree.nodes_iter(data=True) if d.get('split') == 'segment.age']

    for node in switch_header_nodes:
        node_indent = tree.node[node]['indent'].count('\t')
        header_indent = tree.node[node]['switch_header'].count('\t')

        children_indent = [tree.node[c]['indent'].count('\t') for c in tree.successors_iter(node)]

        assert node_indent - 1 == header_indent
        assert all([header_indent + 2 == child_indent for child_indent in children_indent])


def test_compound_feature_presence(graph):
    tree = BonsaiTree(graph)

    text = tree.bonsai.replace('\t', '').split('\n')

    for row in text:
        if 'segment' in row:
            assert any(['segment[{id}]'.format(id=i) in row for i in [12345, 67890, 13579]])


def test_multiple_compound_features(multiple_compound_features_graph):
    feature_value_order = {
        'segment': [1, 2],
        'segment.age': [(0, 10), (10, 20)],
        'advertiser.lifetime_frequency': [(5, 10), (None, 4), (11, 11), (12, None), (0, 10)]
    }

    feature_order = ['segment', 'segment.age', 'advertiser.lifetime_frequency', 'user_day']

    tree = BonsaiTree(
        multiple_compound_features_graph,
        feature_order=feature_order,
        feature_value_order=feature_value_order,
        advertiser=1
    )

    expected_tree = '''
        if segment[1]:
        \tswitch segment[1].age:
        \t\tcase (0 .. 10):
        \t\t\tswitch advertiser[1].lifetime_frequency:
        \t\t\t\tcase (5 .. 10):
        \t\t\t\t\t0.5000
        \t\t\t\tcase ( .. 4):
        \t\t\t\t\t0.3000
        \t\tcase (10 .. 20):
        \t\t\t0.1000
        else segment[2]:
        \tswitch segment[2].age:
        \t\tcase (0 .. 10):
        \t\t\tif advertiser[1].lifetime_frequency = 11:
        \t\t\t\t0.6000
        \t\t\telif advertiser[1].lifetime_frequency >= 12:
        \t\t\t\t0.7000
        \t\t\telif every advertiser[1].lifetime_frequency >= 0, advertiser[1].lifetime_frequency <= 10:
        \t\t\t\t0.9000
        \t\t\telse user_day range (0, 3):
        \t\t\t\t1.0000
    '''.replace(8 * ' ', '').strip().lstrip('\n') + '\n'

    assert tree.bonsai == expected_tree


def test_get_range_output_for_finite_boundary_points(graph):
    some_graph = nx.DiGraph(graph)
    tree = BonsaiTree(some_graph)

    for join in ['any', 'every', None]:
        out = tree._get_range_output_for_finite_boundary_points(0, 1, 'user_hour', join_statement=join)
        assert out == 'user_hour range (0, 1)'

    for join in ['any', 'every', None]:
        out = tree._get_range_output_for_finite_boundary_points(1, 1, 'user_hour', join_statement=join)
        assert out == 'user_hour = 1'

    for join in ['any', 'every', None]:
        out = tree._get_range_output_for_finite_boundary_points(1, 1, 'advertiser[123].recency', join_statement=join)
        assert out == 'advertiser[123].recency = 1'

    for join in ['every', None]:
        out = tree._get_range_output_for_finite_boundary_points(1, 2, 'advertiser[123].recency', join_statement=join)
        assert out == (join is None) * 'every ' + 'advertiser[123].recency >= 1, advertiser[123].recency <= 2'

    join = 'any'
    with pytest.raises(ValueError):
        tree._get_range_output_for_finite_boundary_points(1, 2, 'advertiser[123].recency', join_statement=join)


def test_two_range_features(graph_two_range_features):
    tree = BonsaiTree(graph_two_range_features)

    switch_nodes = [n for n, d in tree.nodes_iter(data=True) if d.get('switch_header')]

    for node in switch_nodes:
        parent = tree.predecessors(node)[0]

        header_indent = tree.node[node]['switch_header'].count('\t')
        parent_indent = tree.node[parent]['indent'].count('\t')

        assert header_indent - 1 == parent_indent


def test_feature_validation(graph_two_range_features):
    tree = BonsaiTree(graph_two_range_features)

    for node, data in tree.nodes_iter(data=True):
        try:
            lower, upper = data['state']['segment.age']
            assert lower >= 0
            assert isinstance(lower, int)
            assert isinstance(upper, int)
        except KeyError:
            pass

    for node, data in tree.nodes_iter(data=True):
        try:
            lower, upper = data['state']['user_hour']

            assert lower >= 0
            assert upper <= 23
            assert isinstance(lower, int)
            assert isinstance(upper, int)
        except KeyError:
            pass

    for parent, _, data in tree.edges_iter(data=True):
        if tree.node[parent]['split'] == 'segment.age':
            try:
                lower, upper = data['value']

                assert lower >= 0
                assert isinstance(lower, int)
                assert isinstance(upper, int)
            except KeyError:
                pass

    for parent, _, data in tree.edges_iter(data=True):
        if tree.node[parent]['split'] == 'user_hour':
            try:
                lower, upper = data['value']

                assert lower >= 0
                assert upper <= 23
                assert isinstance(lower, int)
                assert isinstance(upper, int)
            except KeyError:
                pass


def test_compound_feature(graph_compound_feature):
    tree = BonsaiTree(graph_compound_feature)

    assert 'every site_id=1, placement_id="a":' in tree.bonsai
    assert 'every site_id=1, placement_id="b":' in tree.bonsai


def test_if_elif_else_switch_default(parameterized_graph):
    tree = BonsaiTree(parameterized_graph)

    line_list = tree.bonsai.split('\n')
    line_list = line_list[:-1] if line_list[-1] == '' else line_list
    line_list = [line for line in line_list if 'leaf_name: ' not in line]
    indent_dict = {line: len(line.split('\t')) - 1 for line in line_list}

    indent_list = [indent_dict[i] for i in line_list]
    assert all(indent != next_indent for indent, next_indent in zip(indent_list, indent_list[1:]))

    queue = deque([line_list])

    while len(queue) > 0:
        sub_list = queue.pop()
        indent_list = [indent_dict[i] for i in sub_list]

        outermost_level = min(indent_list)
        indices = [i for i, v in enumerate(indent_list) if v == outermost_level]

        first = sub_list[indices[0]]
        last = sub_list[indices[-1]]
        but_last = [sub_list[i] for i in indices[0:-1]]
        middle = [sub_list[i] for i in indices[1:-1]]

        if_elif_else_level = 'if' in first and 'else:' in last and all('elif' in line for line in middle)
        switch_level = 'switch' in first and len(indices) == 1
        case_level = all('case' in line for line in but_last) and 'default' in last

        assert if_elif_else_level or switch_level or case_level

        for i, j in zip(indices, indices[1:] + [None]):
            new_sublist = sub_list[i + 1:j]
            if len(new_sublist) == 0:
                continue
            elif len(new_sublist) == 1:
                try:
                    assert float(new_sublist[0].strip())
                except ValueError:
                    assert re.match(
                        r"value: (no_bid|\d+\.\d*|compute\(\w+, (\d+\.\d*|_), "
                        r"(\d+\.\d*|_), (\d+\.\d*|_), (\d+\.\d*|_)\))",
                        new_sublist[0].strip()
                    )
            else:
                queue.append(new_sublist)


def test_segment_order(graph):
    tree = BonsaiTree(graph)

    assert 'if segment[12345]' in tree.bonsai
    assert 'elif segment[67890]' in tree.bonsai


def test_segment_order_mapping(graph):
    tree = BonsaiTree(
        graph,
        feature_value_order={
            'segment': [67890, 12345]
        }
    )

    assert 'if segment[67890]' in tree.bonsai
    assert 'elif segment[12345]' in tree.bonsai


def test_language_order_mapping(graph_compound_feature):
    tree = BonsaiTree(
        graph_compound_feature,
        feature_value_order={
            'os': ['windows', 'linux']
        }
    )

    bonsai = tree.bonsai.replace('\n', '').replace('\t', '')

    assert 'if os="windows":0.1000elif os="linux":0.2000' in bonsai


def test_language_order_mapping_one_value(graph_compound_feature):
    tree = BonsaiTree(
        graph_compound_feature,
        feature_value_order={
            'os': ['windows']
        }
    )

    bonsai = tree.bonsai.replace('\n', '').replace('\t', '')

    assert 'if os="windows":0.1000elif os="linux":0.2000' in bonsai


def test_language_segment_age_order(graph):
    tree = BonsaiTree(graph)

    assert 'if segment[12345].age' in tree.bonsai
    assert 'elif language' in tree.bonsai


def test_feature_order_mapping(graph):
    tree = BonsaiTree(
        graph,
        feature_order=['language', 'segment.age']
    )

    # language comes first
    assert 'if language' in tree.bonsai
    # segment.age comes before browser
    assert 'elif segment[12345].age' in tree.bonsai.split('elif browser="safari"')[0]


def test_no_bid_present_in_output(graph):
    tree = BonsaiTree(graph)
    text = tree.bonsai

    assert 'value: no_bid' in text


def test_switch_non_switch_range(small_graph):
    graph = small_graph
    tree = BonsaiTree(graph)

    assert 'switch user_hour' in tree.bonsai
    assert 'switch user_day' in tree.bonsai
    assert 'case ( .. 10)' in tree.bonsai
    assert 'case (11 .. 15)' in tree.bonsai
    assert 'if user_day range (3, 6)' in tree.bonsai


def test_get_range_statement():
    bonsai = BonsaiTree()
    get_range_statement = bonsai._get_range_statement
    values_dict = {1: (None, 1),
                   2: (1.54389, None),
                   3: (0.9, 2.1),
                   4: (None, None),
                   5: (0.99999, 1.4),
                   6: (-float('inf'), 1),
                   7: (1.3, float('inf'))
                   }
    feature = 'some_feature'

    assert get_range_statement(values_dict[1], feature) == 'some_feature <= 1'
    assert get_range_statement(values_dict[2], feature) == 'some_feature >= 1.5439'
    assert get_range_statement(values_dict[3], feature) == 'some_feature range (0.9, 2.1)'
    with pytest.raises(ValueError):
        get_range_statement(values_dict[4], feature)
    assert get_range_statement(values_dict[5], feature) == 'some_feature range (1.0, 1.4)'
    assert get_range_statement(values_dict[6], feature) == 'some_feature <= 1'
    assert get_range_statement(values_dict[7], feature) == 'some_feature >= 1.3'


def test_missing_values(missing_values_graph):
    graph = missing_values_graph

    feature_value_order = {
        'segment': [1, 2],
        'os': [("linux", "osx"), ("linux",)],
        'segment.age': [(0, 10), (10, float('inf'))]
    }

    feature_order = ['segment', 'os']

    tree = BonsaiTree(
        graph,
        feature_order=feature_order,
        feature_value_order=feature_value_order,
        absence_values={'segment': (1, 2)}
    )

    expected_tree = '''
        if segment[1]:
        \tswitch segment[1].age:
        \t\tcase (0 .. 10):
        \t\t\t0.1000
        \t\tcase (10 .. ):
        \t\t\t0.1000
        \t\tdefault:
        \t\t\t0.1000
        elif segment[2]:
        \tif os in ("linux","osx"):
        \t\t0.1000
        \telif os absent:
        \t\t0.1000
        \telse:
        \t\t0.1000
        elif every not segment[1], not segment[2]:
        \tif os in ("linux"):
        \t\t0.1000
        \telse:
        \t\t0.1000
        else:
        \t0.1000
    '''.replace(8 * ' ', '').strip().lstrip('\n') + '\n'

    assert tree.bonsai == expected_tree


def test_missing_values_short(missing_values_graph_short):
    graph = missing_values_graph_short

    feature_value_order = {
        'segment': [1, 2],
        'segment.age': [(0, 10)]
    }

    feature_order = ['segment']

    tree = BonsaiTree(
        graph,
        feature_order=feature_order,
        feature_value_order=feature_value_order,
        absence_values={'segment': (1, 2)}
    )

    expected_tree = '''
        if segment[1]:
        \tswitch segment[1].age:
        \t\tcase (0 .. 10):
        \t\t\t0.1000
        \t\tdefault:
        \t\t\t0.1000
        elif segment[2]:
        \t0.1000
        elif every not segment[1], not segment[2]:
        \t0.1000
        else:
        \t0.1000
    '''.replace(8 * ' ', '').strip().lstrip('\n') + '\n'

    assert tree.bonsai == expected_tree


def test_negated_values(negated_values_graph):
    graph = negated_values_graph

    tree = BonsaiTree(
        graph,
        feature_order=[('segment', 'segment'), ('segment', 'segment', 'segment')],
        feature_value_order={
            ('segment', 'segment'): [(1, 10), (1, 2)]
        }
    )

    expected_conditions = [
        'every segment[1], segment[2]',
        'every segment[1], not segment[2], segment[3]',
        'any segment[1], segment[2]',
        'any segment[1], not segment[10]'
    ]

    assert all([e in tree.bonsai for e in expected_conditions])

    indexes = [tree.bonsai.index(e) for e in expected_conditions]
    assert tree.bonsai.index('any segment[1], not segment[10]') == min(indexes)


def test_feature_slicer(unsliced_graph, small_unsliced_graph):
    tree = BonsaiTree(
        unsliced_graph,
        slice_features=('slice_feature',),
        slice_feature_values={'slice_feature': 'good'}
    )

    assert all(['slice_feature' not in tree.node[n].get('state', set()) for n in tree.node])
    assert all(['slice_feature' not in tree.node[n].get('split', dict()).values() for n in tree.node])

    tree = BonsaiTree(
        small_unsliced_graph,
        slice_features=('slice_feature',),
        slice_feature_values={'slice_feature': 'good'}
    )

    assert all(['slice_feature' not in tree.node[n].get('state', set()) for n in tree.node])
    assert all(['slice_feature' not in tree.node[n].get('split', dict()).values() for n in tree.node])
    assert tree.node[0]['output'] == 5.


def test_feature_slicer_single_wrong_slice_feature_value(small_unsliced_graph_single_slice_feature_value):
    tree = BonsaiTree(
        small_unsliced_graph_single_slice_feature_value,
        slice_features=('slice_feature',),
        slice_feature_values={'slice_feature': 'value'}
    )

    assert all(['slice_feature' not in tree.node[n].get('state', set()) for n in tree.node])
    assert all(['slice_feature' not in tree.node[n].get('split', dict()).values() for n in tree.node])
    assert tree.node[0]['output'] == 5.


def test_feature_slicer_single_correct_slice_feature_value(small_unsliced_graph_single_slice_feature_value):
    tree = BonsaiTree(
        small_unsliced_graph_single_slice_feature_value,
        slice_features=('slice_feature',),
        slice_feature_values={'slice_feature': 'other_value'}
    )

    assert all(['slice_feature' not in tree.node[n].get('state', set()) for n in tree.node])
    assert all(['slice_feature' not in tree.node[n].get('split', dict()).values() for n in tree.node])
    assert tree.node[0]['output'] == 1.


def test_feature_slicer_mixed_split(small_unsliced_graph_mixed_split):
    tree = BonsaiTree(
        small_unsliced_graph_mixed_split,
        slice_features=('slice_feature',),
        slice_feature_values={'slice_feature': 'good'}
    )

    assert all(['slice_feature' not in tree.node[n].get('state', set()) for n in tree.node])
    assert all(['slice_feature' not in tree.node[n].get('split', dict()).values() for n in tree.node])
    assert 'output' not in tree.node[0]
    assert tree.node['default_one']['output'] == 5.
