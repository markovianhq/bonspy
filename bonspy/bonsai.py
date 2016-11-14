# -*- coding: utf-8 -*-

from __future__ import (
    print_function, division, generators,
    absolute_import, unicode_literals
)

import base64

from collections import deque

import networkx as nx

from bonspy.features import compound_features, get_validated


RANGE_EPSILON = 1


class BonsaiTree(nx.DiGraph):
    """
    A NetworkX DiGraph (directed graph) subclass that knows how to print
    itself out in the AppNexus Bonsai bidding tree language.

    See the readme for the expected graph structure:

    https://github.com/mathemads/bonspy

    The Bonsai text representation of this tree is stored in its `bonsai` attribute.
    """

    def __init__(self, graph=None, join_statements=None):
        if graph is not None:
            super(BonsaiTree, self).__init__(graph)
            self._validate_feature_values()
            self._assign_indent()
            self._assign_condition()
            self._handle_switch_statements()
            self.join_statements = join_statements or {}
            self.bonsai = ''.join(self._tree_to_bonsai())
        else:
            super(BonsaiTree, self).__init__()

    @property
    def bonsai_encoded(self):
        return base64.b64encode(self.bonsai.encode('ascii')).decode()

    def _validate_feature_values(self):
        self._validate_node_states()
        self._validate_edge_values()

    def _validate_node_states(self):
        for node, data in self.nodes_iter(data=True):
            for feature, value in data.get('state', {}).items():
                self.node[node]['state'][feature] = get_validated(feature, value)

    def _validate_edge_values(self):
        for parent, child, data in self.edges_iter(data=True):
            feature = self.node[parent]['split']
            try:
                value = data['value']
                self.edge[parent][child]['value'] = get_validated(feature, value)
            except KeyError:
                pass  # edge has no value attribute, nothing to validate

    def _get_root(self):
        for node in self.nodes():
            if len(self.predecessors(node)) == 0:
                return node

    def _assign_indent(self):
        root = self._get_root()
        queue = deque([root])

        self.node[root]['indent'] = ''

        while len(queue) > 0:
            node = queue.popleft()
            indent = self.node[node]['indent']

            next_nodes = self.successors(node)
            for node in next_nodes:
                self.node[node]['indent'] = indent + '\t'

            next_nodes = sorted(next_nodes, key=self._sort_key)

            queue.extend(next_nodes)

    def _sort_key(self, x):
        return self.node[x].get('is_default_leaf', False), self.node[x].get('is_default_node', False), x

    def _assign_condition(self):
        root = self._get_root()
        queue = deque([root])

        while len(queue) > 0:
            node = queue.popleft()

            next_nodes = self.successors(node)
            next_nodes = sorted(next_nodes, key=self._sort_key)

            for n_i, n in enumerate(next_nodes):
                if n_i == 0:
                    condition = 'if'
                elif n_i == len(next_nodes) - 1:
                    condition = 'else'
                else:
                    condition = 'elif'

                self.node[n]['condition'] = condition

            queue.extend(next_nodes)

    def _handle_switch_statements(self):
        self._assign_switch_headers()
        self._adapt_switch_indentation()
        self._adapt_switch_header_indentation()

    def _assign_switch_headers(self):
        root = self._get_root()
        stack = deque(self._get_sorted_out_edges(root))

        while stack:
            parent, child = stack.popleft()

            next_edges = self._get_sorted_out_edges(child)
            stack.extendleft(next_edges[::-1])  # extendleft reverses order!

            type_ = self.edge[parent][child].get('type')

            if type_ == 'range':
                feature = self._get_feature(parent, state_node=parent)

                header = 'switch {}:'.format(feature)  # appropriate indentation added later

                self.node[parent]['switch_header'] = header

    def _adapt_switch_indentation(self):
        switch_header_nodes = [n for n, d in self.nodes_iter(data=True) if d.get('switch_header')]
        stack = deque(switch_header_nodes)

        while stack:
            node = stack.popleft()
            next_nodes = self.successors(node)
            stack.extendleft(next_nodes[::-1])  # extendleft reverses order!

            self.node[node]['indent'] += '\t'

    def _adapt_switch_header_indentation(self):
        for node, data in self.nodes_iter(data=True):
            if data.get('switch_header'):
                parent = self.predecessors(node)[0]
                parent_indent = self.node[parent]['indent']
                switch_header = self.node[node]['switch_header']
                self.node[node]['switch_header'] = parent_indent + '\t' + switch_header

    def _get_sorted_out_edges(self, node):
        edges = self.out_edges_iter(node)
        keys = {'if': 0, 'elif': 1, 'else': 2}
        edges = sorted(edges, key=lambda x: keys[self.node[x[1]]['condition']])
        return edges

    def _get_output_text(self, node):
        out_text = ''
        if self.node[node].get('is_leaf') or self.node[node].get('is_default_leaf'):
            out_value = self.node[node]['output']
            out_indent = self.node[node]['indent']
            out_text = '{indent}{value:.4f}\n'.format(indent=out_indent, value=out_value)

        return out_text

    def _get_conditional_text(self, parent, child):
        pre_out = self._get_pre_out_statement(parent, child)
        out = self._get_out_statement(parent, child)

        return pre_out + out

    def _get_pre_out_statement(self, parent, child):
        type_ = self.edge[parent][child].get('type')
        conditional = self.node[child]['condition']

        pre_out = ''

        if type_ == 'range' and conditional == 'if':
            pre_out = self.node[parent]['switch_header'] + '\n'

        return pre_out

    def _get_out_statement(self, parent, child):
        indent = self.node[parent]['indent']
        value = self.edge[parent][child].get('value')
        type_ = self.edge[parent][child].get('type')
        conditional = self.node[child]['condition']

        feature = self._get_feature(parent, child)

        if self.node[parent].get('switch_header'):
            out = self._get_range_statement(indent, value)
        else:
            out = '{indent}{conditional}'
            if type_ is not None and all(isinstance(x, (list, tuple)) for x in (feature, type_)):
                join_statement = self._get_join_statement(feature)
                out += ' ' + join_statement + ' ' + ', '.join(
                    self._get_if_conditional(indent, v, t, f) for v, t, f in zip(value, type_, feature)
                )
            elif type_ is not None and not any(isinstance(x, (list, tuple)) for x in (feature, type_)):
                out += ' ' + self._get_if_conditional(indent, value, type_, feature)
            elif type_ is None:
                out += ''
            else:
                raise ValueError(
                    'Unable to deduce if-conditional '
                    'for feature "{}" and type "{}".'.format(
                        feature, type_
                    )
                )
            out += ':\n'

            out = out.format(indent=indent, conditional=conditional)

        return out

    def _get_join_statement(self, feature):
        return self.join_statements.get(feature, 'every')

    def _get_feature(self, parent, state_node):
        feature = self.node[parent].get('split')
        if isinstance(feature, (list, tuple)):
            return self._get_formatted_multidimensional_compound_feature(feature, state_node)
        elif '.' in feature:
            return self._get_formatted_compound_feature(feature, state_node)
        else:
            return feature

    def _get_formatted_multidimensional_compound_feature(self, feature, state_node):
        attribute_indices = self._get_attribute_indices(feature)
        feature = list(feature)
        for i in attribute_indices:
            feature[i] = self._get_formatted_compound_feature(feature[i], state_node)

        return tuple(feature)

    @staticmethod
    def _get_attribute_indices(feature):
        return [feature.index(f) for f in feature if '.' in f and f.split('.')[0] in feature]

    def _get_formatted_compound_feature(self, feature, state_node):
        object_, attribute = feature.split('.')
        feature = '{feature}[{value}].{attribute}'.format(
            feature=object_,
            value=self.node[state_node]['state'][object_],
            attribute=attribute
        )

        return feature

    @staticmethod
    def _get_range_statement(indent, value, feature=None):
        left_bound, right_bound = value
        try:
            left_bound = int(left_bound)
        except TypeError:
            left_bound = ''
        try:
            right_bound = int(right_bound)
        except TypeError:
            right_bound = ''

        if left_bound == right_bound == '':
            raise ValueError(
                'Value "{}" not reasonable as value of a range feature.'.format(
                    value
                )
            )

        if feature is None:
            out = '{indent}case ({left_bound} .. {right_bound}):\n'.format(
                indent=indent,
                left_bound=left_bound,
                right_bound=right_bound
            )
        else:
            out = '{feature} in ({left_bound} .. {right_bound})'.format(
                feature=feature,
                left_bound=left_bound,
                right_bound=right_bound
            )

        return out

    def _get_if_conditional(self, indent, value, type_, feature):
        if type_ == 'range':
            out = self._get_range_statement(indent, value, feature)
        elif type_ == 'membership':
            value = tuple(value)
            if isinstance(value[0], str):
                value = '(\"{}\")'.format('\",\"'.join(value))
            out = '{feature} in {value}'.format(
                feature=feature,
                value=value
            )
        elif type_ == 'assignment':
            comparison = '='
            value = '"{}"'.format(value) if not self._is_numerical(value) else value

            if feature.split('.')[0] not in compound_features:
                out = '{feature}{comparison}{value}'.format(
                    feature=feature,
                    comparison=comparison,
                    value=value
                )
            elif feature in compound_features:
                out = '{feature}[{value}]'.format(
                    feature=feature,
                    value=value
                )
            else:
                object_, attribute = feature.split('.')
                out = '{feature}[{value}].{attribute}'.format(
                    feature=object_,
                    value=value,
                    attribute=attribute
                )

        else:
            raise ValueError(
                'Unable to deduce conditional statement for type "{}".'.format(type_)
            )

        return out

    def _get_default_conditional_text(self, parent, child):
        type_ = self._get_sibling_type(parent, child)
        indent = self.node[parent]['indent']

        conditional = 'default' if type_ == 'range' else 'else'

        return '{indent}{conditional}:\n'.format(indent=indent, conditional=conditional)

    def _get_edge_siblings(self, parent, child):
        this_edge = (parent, child)
        sibling_edges = [edge for edge in self.out_edges(parent) if edge != this_edge]

        return sibling_edges

    def _get_sibling_type(self, parent, child):
        sibling_edges = self._get_edge_siblings(parent, child)
        sibling_types = [self.edge[sibling_parent][sibling_child]['type']
                         for sibling_parent, sibling_child in sibling_edges]

        return sibling_types[0]

    def _tree_to_bonsai(self):
        root = self._get_root()
        stack = deque(self._get_sorted_out_edges(root))

        while len(stack) > 0:
            parent, child = stack.popleft()

            next_edges = self._get_sorted_out_edges(child)
            stack.extendleft(next_edges[::-1])  # extendleft reverses order!

            if not self.node[child].get('is_default_leaf', False):
                conditional_text = self._get_conditional_text(parent, child)
            elif self.node[child].get('is_default_leaf', False):
                conditional_text = self._get_default_conditional_text(parent, child)

            out_text = self._get_output_text(child)

            yield conditional_text + out_text

    @staticmethod
    def _is_numerical(x):
        try:
            int(x)
            float(x)
            return True
        except ValueError:
            return False
