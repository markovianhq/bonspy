from abc import ABCMeta, abstractmethod
from collections import OrderedDict, defaultdict
from csv import DictReader
import gzip
from glob import glob

import networkx as nx
import pandas as pd


class GraphBuilder:

    def __init__(self, input_, features, lazy_formatters=(), types_dict={}):
        """
        :param input_: str or list of str, path to gzipped csv input
        :param features: iterable, ordered features to build the tree with
        :param lazy_formatters: tuple of tuples, e.g. (('os', str), (user_day, int))
        :param types_dict: dict, types to be used for split, defaults to "assignment"
        """
        self.input_ = glob(input_) if isinstance(input_, str) else input_
        self.features = features
        self.types_iterable = self._get_types_iterable(types_dict)
        self.lazy_formatters = self._get_lazy_formatter(lazy_formatters)
        self.edge_map_ = None

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

    def get_graph(self, graph=None, edge_map=None):
        graph, node_index = self._seed_graph(graph)
        self._get_edge_map_from_file(edge_map=edge_map)

        data = self.get_data()
        for row in data:
            graph, node_index = self._add_branch(graph, row, node_index)

        return graph

    @staticmethod
    def _seed_graph(graph):
        if not graph:
            graph = nx.DiGraph()
            root = (0, 0)
            graph.add_node(root, state=OrderedDict())
        node_index = 1 + max((n[0] for n in graph.nodes_iter()))
        return graph, node_index

    def _get_edge_map_from_file(self, edge_map=None):
        self.edge_map_ = edge_map
        for file in self.input_:
            x = pd.read_csv(
                file, usecols=self.features, compression='gzip', engine='c', dtype=str
            ).fillna(value='')[self.features].values
            self._partial_fit_edge_map_(x)
            del x

    def _partial_fit_edge_map_(self, x):
        if self.edge_map_ is None:
            self._fit_edge_map(x)
        else:
            for i, col in enumerate(x.T):
                old_keys = set(self.edge_map_[i].keys())
                new_keys = set(col).difference(old_keys)
                old_max_index = max(self.edge_map_[i].values())
                self.edge_map_[i].update({key: i for i, key in enumerate(new_keys, start=old_max_index + 1)})

    def _fit_edge_map(self, x):
        self.edge_map_ = []
        for col in x.T:
            uniques = set(col)
            self.edge_map_.append({key: i for i, key in enumerate(uniques)})

    def _add_branch(self, graph, row, node_index):
        parent = (0, 0)
        graph.node[parent] = self._apply_functions(graph.node[parent], row)

        for feature in self.features:
            feature_value = row[feature]
            enc_feature_value = self._get_enc_feature_value(feature, feature_value)

            child = self._get_child(graph, parent, enc_feature_value)
            if not child:

                childless = self._check_if_childless(graph, parent)
                if childless:
                    default_leaf = (node_index, -1)
                    state = self._get_state(graph, parent)
                    graph = self._add_node(graph, default_leaf, state, is_default_leaf=True)
                    node_index += 1

                child = self._get_node_id(feature, feature_value, node_index)
                state = self._get_state(graph, parent, new_feature=(feature, feature_value))
                graph = self._add_node(graph, child, state)
                graph = self._connect_node_to_parent(graph, parent, child, feature, feature_value)
                graph = self._update_parent_split(graph, parent, feature)
                node_index += 1

            graph.node[child] = self._apply_functions(graph.node[child], row)
            parent = child
        else:
            graph.node[child]['is_leaf'] = True

        return graph, node_index

    def _get_enc_feature_value(self, feature, feature_value):
        feature_index = self.features.index(feature)
        feature_mapping = self.edge_map_[feature_index]
        try:
            enc_feature_value = feature_mapping[feature_value]
        except KeyError:  # numpy and pandas don't support NaN values in int columns
            feature_value_ = str(float(feature_value))
            enc_feature_value = feature_mapping[feature_value_]
        return enc_feature_value

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

    @staticmethod
    def _add_node(graph, new_node, state, **kwargs):
        graph.add_node(new_node, state=state, **kwargs)
        return graph

    @staticmethod
    def _get_child(graph, parent, enc_feature_value):
        edges = graph.edges_iter(parent)
        children = (child for _, child in edges)
        try:
            child = next(child for child in children if child[1] == enc_feature_value)
        except StopIteration:
            child = None
        return child

    def _get_node_id(self, feature, feature_value, node_index):
        enc_feature_value = self._get_enc_feature_value(feature, feature_value)
        new_node = (node_index, enc_feature_value)
        return new_node

    def _connect_node_to_parent(self, graph, parent, new_node, feature, feature_value):
        feature_index = self.features.index(feature)
        type_ = self.types_iterable[feature_index]
        graph.add_edge(parent, new_node, type=type_, value=feature_value)
        return graph

    @staticmethod
    def _update_parent_split(graph, parent, feature):
        graph.node[parent]['split'] = feature
        return graph

    def _add_new_feature(self, state, new_feature):
        feature, value = new_feature
        formatter = self._get_formatter(self.lazy_formatters[feature])
        state[feature] = formatter(value)
        return state

    @staticmethod
    def _get_formatter(formatter):
        return lambda x: formatter(x) if len(x) > 0 else None


class Bidder(metaclass=ABCMeta):

    def __int__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def compute_bids(self, graph):
        leaves = self.get_leaves(graph)
        for leaf in leaves:
            kwarg = self.get_bid(graph=graph, leaf=leaf)
            for key, value in kwarg.items():
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
        super(ConstantBidder, self).__init__(**kwargs)
        self.bid = bid

    def get_bid(self, *args, **kwargs):
        return {'output': self.bid}


class EstimatorBidder(Bidder):

    def __init__(self, base_bid=1., estimators=(), **kwargs):
        super(EstimatorBidder, self).__init__(**kwargs)
        self.base_bid = base_bid
        self.estimators = estimators

    def get_bid(self, *args, **kwargs):
        graph = kwargs['graph']
        leaf = kwargs['leaf']
        state = graph.node[leaf]['state']
        bid = self.base_bid
        for estimator in self.estimators:
            x = estimator.dict_vectorizer(state)
            bid *= estimator.predict(x)
        return {'output': bid}
