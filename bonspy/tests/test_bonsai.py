# -*- coding: utf-8 -*-

from __future__ import (
    print_function, division, generators,
    absolute_import, unicode_literals
)

from collections import deque

from bonspy import BonsaiTree


def test_switch_header(graph):
    tree = BonsaiTree(graph)
    text = tree.bonsai.replace('\t', '').split('\n')

    switch_header_nodes = [d for _, d in tree.nodes_iter(data=True) if d.get('split') == 'segment.age']

    assert len(switch_header_nodes) == 2
    assert all([d.get('switch_header') is not None for d in switch_header_nodes])

    for row in text:
        if 'segment.age' in row:
            assert row in ['switch segment[12345].age:', 'switch segment[67890].age:']


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
        if 'segment' in row and 'segment.age' not in row:
            assert 'segment[12345]' in row or 'segment[67890]' in row


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

    assert 'if every site_id=1, placement_id="a":' in tree.bonsai
    assert 'elif every site_id=1, placement_id="b":' in tree.bonsai


def test_if_elif_else_switch_default(parameterized_graph):
    tree = BonsaiTree(parameterized_graph)

    line_list = tree.bonsai.split('\n')
    line_list = line_list[:-1] if line_list[-1] == '' else line_list
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
            new_sublist = sub_list[i+1:j]
            if len(new_sublist) == 0:
                continue
            elif len(new_sublist) == 1:
                assert float(new_sublist[0].strip())
            else:
                queue.append(new_sublist)
