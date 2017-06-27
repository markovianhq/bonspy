from abc import ABCMeta, abstractmethod
from collections import OrderedDict, defaultdict
from csv import DictReader
import gzip
from glob import glob

import networkx as nx


class GraphBuilder:

    def __init__(self, input_, features, lazy_formatters=(), types_dict={}, functions=()):
        """
        :param input_: str or list of str, path to gzipped csv input
        :param features: iterable, ordered features to build the tree with
        :param lazy_formatters: tuple of tuples, e.g. (('os', str), (user_day, int)) or dict
        :param types_dict: dict, types to be used for split, defaults to "assignment"
        :param functions: iterable, functions that return node_dict and take node_dict and row as arguments
        """
        self.input_ = glob(input_) if isinstance(input_, str) else input_
        self.features = features
        self.types_iterable = self._get_types_iterable(types_dict)
        self.lazy_formatters = self._get_lazy_formatter(lazy_formatters)
        self.functions = functions

    def _get_types_iterable(self, types_dict):
        return tuple(types_dict.get(f, 'assignment') for f in self.features)

    @staticmethod
    def _get_lazy_formatter(formatters):
        if not formatters:
            return defaultdict(lambda: (lambda x: x))
        else:
            lazy_formatters = defaultdict(lambda: str)
            lazy_formatters.update(formatters)
            return lazy_formatters

    def get_data(self):
        for file in self.input_:
            data = DictReader(gzip.open(file, 'rt', encoding='utf-8'))
            yield from data

    def get_graph(self, graph=None):
        graph, node_index = self._seed_graph(graph)

        data = self.get_data()
        for row in data:
            graph, node_index = self._add_branch(graph, row, node_index)

        return graph

    @staticmethod
    def _seed_graph(graph):
        if not graph:
            graph = nx.DiGraph()
            root = 0
            graph.add_node(root, state=OrderedDict())
        node_index = 1 + max((n for n in graph.nodes_iter()))
        return graph, node_index

    def _add_branch(self, graph, row, node_index):
        parent = 0
        graph.node[parent] = self._apply_functions(graph.node[parent], row)

        for feature in self.features:
            feature_value = row[feature]
            child = self._get_child(graph, parent, feature, feature_value)
            if child is None:

                childless = self._check_if_childless(graph, parent)
                if childless:
                    default_leaf = node_index
                    state = self._get_state(graph, parent)
                    graph.add_node(default_leaf, state=state, is_default_leaf=True)
                    graph.add_edge(parent, default_leaf)
                    node_index += 1

                child = node_index
                state = self._get_state(graph, parent, new_feature=(feature, feature_value))
                graph.add_node(child, state=state)
                graph = self._connect_node_to_parent(graph, parent, child, feature, feature_value)
                graph = self._update_parent_split(graph, parent, feature)
                node_index += 1

            graph.node[child] = self._apply_functions(graph.node[child], row)
            parent = child
        else:
            graph.node[child]['is_leaf'] = True

        return graph, node_index

    @staticmethod
    def _check_if_childless(graph, parent):
        edges = graph.edges_iter(parent)
        try:
            _ = next(edges)  # NOQA
            return False
        except StopIteration:
            return True

    def _get_state(self, graph, parent, new_feature=None):
        state = graph.node[parent]['state'].copy()
        new_state = self._add_new_feature(state, new_feature) if new_feature else state
        return new_state

    def _get_child(self, graph, parent, feature, feature_value):
        edges = graph.edges_iter(parent, data=True)
        children = ((child, data) for _, child, data in edges if data)  # filter out default leaves
        formatter = self._get_formatter(self.lazy_formatters[feature])
        try:
            child = next(child for child, data in children if data.get('value') == formatter(feature_value))
        except StopIteration:
            child = None
        return child

    def _connect_node_to_parent(self, graph, parent, new_node, feature, feature_value):
        feature_index = self.features.index(feature)
        type_ = self.types_iterable[feature_index]
        formatter = self._get_formatter(self.lazy_formatters[feature])
        graph.add_edge(parent, new_node, type=type_, value=formatter(feature_value))
        return graph

    @staticmethod
    def _update_parent_split(graph, parent, feature):
        graph.node[parent]['split'] = feature
        return graph

    def _apply_functions(self, node_dict, row):
        for function_ in self.functions:
            node_dict = function_(node_dict, row)
        return node_dict

    def _add_new_feature(self, state, new_feature):
        feature, value = new_feature
        formatter = self._get_formatter(self.lazy_formatters[feature])
        state[feature] = formatter(value)
        return state

    @staticmethod
    def _get_formatter(formatter):
        return lambda x: formatter(x) if len(x) > 0 else None


class Bidder(metaclass=ABCMeta):

    def compute_bids(self, graph):
        leaves = self.get_leaves(graph)
        for leaf in leaves:
            output_dict = self.get_bid(graph=graph, leaf=leaf)
            for key, value in output_dict.items():
                graph.node[leaf][key] = value
        return graph

    @abstractmethod
    def get_bid(self, *args, **kwargs):
        pass

    @staticmethod
    def get_leaves(graph):
        leaves = (
            n for n in graph.nodes_iter() if graph.node[n].get('is_leaf', graph.node[n].get('is_default_leaf', False))
        )
        return leaves


class ConstantBidder(Bidder):

    def __init__(self, bid=1., **kwargs):
        self.bid = bid
        for key, value in kwargs.items():
            setattr(self, key, value)

    def get_bid(self, *args, **kwargs):
        return {'output': self.bid}


class EstimatorBidder(Bidder):

    def __init__(self, base_bid=1., estimators=(), **kwargs):
        self.base_bid = base_bid
        self.estimators = estimators
        for key, value in kwargs.items():
            setattr(self, key, value)

    def get_bid(self, *args, **kwargs):
        graph = kwargs['graph']
        leaf = kwargs['leaf']
        state = graph.node[leaf]['state']
        bid = self.base_bid
        for estimator in self.estimators:
            x = estimator.dict_vectorizer(state, **self.__dict__)
            bid *= estimator.predict(x)
        return {'output': bid}
